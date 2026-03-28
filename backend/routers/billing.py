import logging
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from core.config import get_settings
from db import get_db
from deps import get_agency_user
from models import Campaign, User

router = APIRouter()
logger = logging.getLogger(__name__)


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


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(default=None, alias="stripe-signature"),
):
    """Stripe sends raw body; verify signature and update campaign payment state."""
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
    from models import Campaign

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        campaign_id = metadata.get("campaign_id")
        user_id = metadata.get("user_id")
        price_id = metadata.get("price_id")

        db = SessionLocal()
        try:
            # 1. Update Campaign (if applicable)
            if campaign_id:
                row = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                if row:
                    row.status = "paid"
                    row.stripe_checkout_session_id = session.get("id")
                    db.commit()
                    logger.info("campaign %s marked paid via Stripe", campaign_id)

            # 2. Update User Quotas (if applicable)
            if user_id:
                u_row = db.query(User).filter(User.id == user_id).first()
                if u_row:
                    c_quota, t_quota = settings.get_quotas_for_price(price_id)
                    u_row.monthly_campaign_quota = c_quota
                    u_row.monthly_token_quota = t_quota
                    db.commit()
                    logger.info("user %s quotas updated via price %s", user_id, price_id)
        finally:
            db.close()

    return {"received": True, "type": event.get("type")}
