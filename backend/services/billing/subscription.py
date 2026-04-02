"""
Stripe recurring‑subscription service for AIMOS.

Handles:
  • Customer creation / reuse
  • Subscription checkout session creation (mode=subscription)
  • Webhook processing: invoice.paid, subscription.updated/deleted
  • Billing portal session creation
"""
from __future__ import annotations

import logging
from typing import Optional

import stripe
from sqlalchemy.orm import Session

from core.config import TIER_QUOTA_MAP, get_settings
from models import User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stripe_init() -> None:
    """Lazily set the Stripe key (called before each Stripe API call)."""
    settings = get_settings()
    stripe.api_key = settings.stripe_secret_key


def get_or_create_stripe_customer(db: Session, user: User) -> str:
    """
    Return the user's Stripe Customer ID; create one if it doesn't exist yet.
    Persists the `cus_xxx` back to `user.stripe_customer_id`.
    """
    if user.stripe_customer_id:
        return user.stripe_customer_id

    _stripe_init()
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name or user.email,
        metadata={"aimos_user_id": user.id},
    )
    user.stripe_customer_id = customer.id
    db.commit()
    logger.info("stripe_customer_created user=%s cus=%s", user.id, customer.id)
    return customer.id


# ---------------------------------------------------------------------------
# Subscription Checkout
# ---------------------------------------------------------------------------

def create_subscription_checkout(
    db: Session,
    user: User,
    *,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """
    Creates a Stripe Checkout Session in **subscription** mode.
    Returns {"checkout_session_id", "url"}.
    """
    _stripe_init()
    customer_id = get_or_create_stripe_customer(db, user)

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "aimos_user_id": user.id,
            "price_id": price_id,
        },
        subscription_data={
            "metadata": {
                "aimos_user_id": user.id,
                "price_id": price_id,
            },
        },
    )
    logger.info(
        "subscription_checkout_created user=%s price=%s session=%s",
        user.id, price_id, session.id,
    )
    return {"checkout_session_id": session.id, "url": session.url}


# ---------------------------------------------------------------------------
# Billing Portal
# ---------------------------------------------------------------------------

def create_billing_portal_session(db: Session, user: User, return_url: str) -> dict:
    """
    Creates a Stripe Billing Portal session so users can manage their subscription.
    Returns {"url"}.
    """
    _stripe_init()
    customer_id = get_or_create_stripe_customer(db, user)
    portal = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return {"url": portal.url}


# ---------------------------------------------------------------------------
# Current Subscription Info
# ---------------------------------------------------------------------------

def get_subscription_info(user: User) -> dict:
    """Return the user's current subscription state for the frontend."""
    settings = get_settings()
    tier = user.subscription_tier or "free"
    quotas = TIER_QUOTA_MAP.get(tier, TIER_QUOTA_MAP["free"])
    return {
        "tier": tier,
        "status": user.subscription_status or "none",
        "stripe_customer_id": user.stripe_customer_id,
        "stripe_subscription_id": user.stripe_subscription_id,
        "quotas": {
            "monthly_campaigns": quotas[0] if quotas[0] >= 0 else "unlimited",
            "monthly_tokens": quotas[1] if quotas[1] >= 0 else "unlimited",
        },
        "available_tiers": {
            slug: {
                "campaigns": q[0] if q[0] >= 0 else "unlimited",
                "tokens": q[1] if q[1] >= 0 else "unlimited",
            }
            for slug, q in TIER_QUOTA_MAP.items()
        },
    }


# ---------------------------------------------------------------------------
# Webhook Handlers
# ---------------------------------------------------------------------------

def _apply_tier_to_user(db: Session, user: User, tier: str, status: str) -> None:
    """Set the user's subscription tier/status and sync quotas."""
    user.subscription_tier = tier
    user.subscription_status = status
    quotas = TIER_QUOTA_MAP.get(tier, TIER_QUOTA_MAP["free"])
    user.monthly_campaign_quota = quotas[0]
    user.monthly_token_quota = quotas[1]
    db.commit()
    logger.info(
        "tier_applied user=%s tier=%s status=%s cq=%s tq=%s",
        user.id, tier, status, quotas[0], quotas[1],
    )


def _find_user_by_customer(db: Session, customer_id: str) -> Optional[User]:
    return db.query(User).filter(User.stripe_customer_id == customer_id).first()


def _find_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def handle_invoice_paid(db: Session, event_data: dict) -> None:
    """
    Stripe event: invoice.paid
    Activates / renews the subscription tier for the billed customer.
    """
    invoice = event_data.get("object", {})
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")

    if not customer_id:
        logger.warning("invoice.paid: no customer_id in payload")
        return

    user = _find_user_by_customer(db, customer_id)
    if not user:
        logger.warning("invoice.paid: no user for customer %s", customer_id)
        return

    # Resolve tier from subscription items
    settings = get_settings()
    price_id = None
    lines = invoice.get("lines", {}).get("data", [])
    if lines:
        price_obj = lines[0].get("price", {})
        price_id = price_obj.get("id") if isinstance(price_obj, dict) else None

    tier = settings.get_tier_for_price(price_id)
    user.stripe_subscription_id = subscription_id
    _apply_tier_to_user(db, user, tier, "active")


def handle_subscription_updated(db: Session, event_data: dict) -> None:
    """
    Stripe event: customer.subscription.updated
    Handles plan changes (upgrade/downgrade) and status transitions.
    """
    sub = event_data.get("object", {})
    customer_id = sub.get("customer")
    status = sub.get("status", "active")  # active | past_due | canceled | trialing

    if not customer_id:
        return

    user = _find_user_by_customer(db, customer_id)
    if not user:
        logger.warning("subscription.updated: no user for customer %s", customer_id)
        return

    # Resolve new tier from items
    settings = get_settings()
    price_id = None
    items = sub.get("items", {}).get("data", [])
    if items:
        price_obj = items[0].get("price", {})
        price_id = price_obj.get("id") if isinstance(price_obj, dict) else None

    tier = settings.get_tier_for_price(price_id)
    user.stripe_subscription_id = sub.get("id")

    # Map Stripe status to our internal status
    status_map = {
        "active": "active",
        "past_due": "past_due",
        "canceled": "canceled",
        "trialing": "trialing",
        "incomplete": "none",
        "incomplete_expired": "canceled",
        "unpaid": "past_due",
        "paused": "canceled",
    }
    internal_status = status_map.get(status, "active")

    if internal_status == "canceled":
        _apply_tier_to_user(db, user, "free", "canceled")
    else:
        _apply_tier_to_user(db, user, tier, internal_status)


def handle_subscription_deleted(db: Session, event_data: dict) -> None:
    """
    Stripe event: customer.subscription.deleted
    Downgrades the user to the free tier.
    """
    sub = event_data.get("object", {})
    customer_id = sub.get("customer")
    if not customer_id:
        return

    user = _find_user_by_customer(db, customer_id)
    if not user:
        return

    user.stripe_subscription_id = None
    _apply_tier_to_user(db, user, "free", "canceled")
    logger.info("subscription_deleted user=%s downgraded_to_free", user.id)
