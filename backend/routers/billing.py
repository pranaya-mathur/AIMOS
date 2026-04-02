import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from core.config import get_settings
from db import get_db
from deps import get_agency_user, get_current_user
from models import Campaign, User

router = APIRouter()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# One-time Checkout (existing — unchanged)
# ---------------------------------------------------------------------------


class CheckoutSessionBody(BaseModel):
    """Create a Stripe Checkout Session that tags `campaign_id` in metadata (for webhook → `paid`)."""

    campaign_id: str = Field(..., description="Existing campaign UUID from POST /campaign/create")
    success_url: HttpUrl = Field(..., description="Redirect after payment; may include {CHECKOUT_SESSION_ID}")
    cancel_url: HttpUrl = Field(..., description="Redirect if user cancels checkout")
    price_id: Optional[str] = Field(
        default=None,
        description="Stripe Price ID; defaults to STRIPE_DEFAULT_PRICE_ID in environment",
    )


@router.post("/checkout/session")
def create_checkout_session(
    body: CheckoutSessionBody,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_agency_user),
):
    """Returns `url` to open Stripe Checkout (e.g. Bubble: open external URL or redirect)."""
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured (STRIPE_SECRET_KEY)")

    price_id = body.price_id or settings.stripe_default_price_id
    if not price_id:
        raise HTTPException(
            status_code=400,
            detail="Provide price_id in body or set STRIPE_DEFAULT_PRICE_ID",
        )

    row = db.query(Campaign).filter(Campaign.id == body.campaign_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if user and row.user_id and row.user_id != user.id and user.role != "platform_admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    if not user and not settings.auth_disabled_flag:
        raise HTTPException(status_code=401, detail="Authentication required")

    import stripe

    stripe.api_key = settings.stripe_secret_key

    success = str(body.success_url)
    if "{CHECKOUT_SESSION_ID}" not in success:
        sep = "&" if "?" in success else "?"
        success = f"{success}{sep}session_id={{CHECKOUT_SESSION_ID}}"

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success,
        cancel_url=str(body.cancel_url),
        client_reference_id=body.campaign_id,
        metadata={
            "campaign_id": body.campaign_id,
            "user_id": user.id if user else None,
            "price_id": price_id,
        },
    )

    row.status = "pending_payment"
    row.stripe_checkout_session_id = session.id
    db.commit()

    return {
        "checkout_session_id": session.id,
        "url": session.url,
        "campaign_id": body.campaign_id,
    }


# ---------------------------------------------------------------------------
# Recurring Subscription Endpoints
# ---------------------------------------------------------------------------


class SubscribeBody(BaseModel):
    """Create a Stripe Subscription checkout for a recurring tier."""

    price_id: str = Field(..., description="Stripe recurring Price ID (price_xxx)")
    success_url: HttpUrl = Field(..., description="Redirect after subscription checkout completes")
    cancel_url: HttpUrl = Field(..., description="Redirect if user cancels")


@router.post("/subscribe")
def subscribe(
    body: SubscribeBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a Stripe Checkout Session in **subscription** mode.
    Returns `{url}` to redirect the user to Stripe's hosted checkout page.
    """
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    from services.billing.subscription import create_subscription_checkout

    result = create_subscription_checkout(
        db,
        user,
        price_id=body.price_id,
        success_url=str(body.success_url),
        cancel_url=str(body.cancel_url),
    )
    return result


@router.get("/subscription")
def get_subscription(
    user: User = Depends(get_current_user),
):
    """Return the current user's subscription tier, status, and quotas."""
    from services.billing.subscription import get_subscription_info

    return get_subscription_info(user)


class PortalBody(BaseModel):
    return_url: HttpUrl = Field(..., description="URL to return to after portal session")


@router.post("/portal")
def create_portal(
    body: PortalBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a Stripe Billing Portal session for self-service subscription management.
    Returns `{url}`.
    """
    settings = get_settings()
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    from services.billing.subscription import create_billing_portal_session

    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription to manage")

    return create_billing_portal_session(db, user, str(body.return_url))


# ---------------------------------------------------------------------------
# Stripe Webhook (unified — handles both one-time & subscription events)
# ---------------------------------------------------------------------------


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(default=None, alias="stripe-signature"),
):
    """Stripe sends raw body; verify signature and route event to the appropriate handler."""
    settings = get_settings()
    if not settings.stripe_webhook_secret or not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    import stripe

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        if settings.stripe_webhook_secret == "test_bypass":
            import json

            event = json.loads(payload)
            logger.info("Stripe signature verification bypassed (test_bypass)")
        else:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {exc}") from exc
    except stripe.error.SignatureVerificationError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    from db import SessionLocal
    from models import Campaign, User
    from services.billing.subscription import (
        handle_invoice_paid,
        handle_subscription_deleted,
        handle_subscription_updated,
    )

    event_type = event.get("type", "")
    event_data = event.get("data", {})

    db = SessionLocal()
    try:
        # ── One-time checkout completion (existing logic) ──
        if event_type == "checkout.session.completed":
            session = event_data.get("object", {})
            metadata = session.get("metadata", {})
            campaign_id = metadata.get("campaign_id")
            user_id = metadata.get("user_id")
            price_id = metadata.get("price_id")

            # Campaign payment flow
            if campaign_id:
                row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                if row:
                    row.status = "paid"
                    row.stripe_checkout_session_id = session.get("id")
                    db.commit()
                    logger.info("campaign %s marked paid via Stripe", campaign_id)

            # Legacy quota update via checkout (one-time)
            if user_id and not session.get("subscription"):
                u_row = db.query(User).filter(User.id == user_id).first()
                if u_row:
                    c_quota, t_quota = settings.get_quotas_for_price(price_id)
                    u_row.monthly_campaign_quota = c_quota
                    u_row.monthly_token_quota = t_quota
                    db.commit()
                    logger.info("user %s quotas updated via price %s", user_id, price_id)

        # ── Recurring subscription events ──
        elif event_type == "invoice.paid":
            handle_invoice_paid(db, event_data)

        elif event_type == "customer.subscription.updated":
            handle_subscription_updated(db, event_data)

        elif event_type == "customer.subscription.deleted":
            handle_subscription_deleted(db, event_data)

        else:
            logger.debug("stripe_webhook: unhandled event_type=%s", event_type)

    finally:
        db.close()

    return {"received": True, "type": event_type}
