from __future__ import annotations

import uuid
from calendar import monthrange
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.config import Settings, get_settings
from models import Campaign, UsageEvent, User
from services.usage.exceptions import QuotaExceededError


def _utc_month_bounds(now: datetime | None = None) -> tuple[datetime, datetime]:
    dt = now or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last = monthrange(dt.year, dt.month)[1]
    end = dt.replace(day=last, hour=23, minute=59, second=59, microsecond=999999)
    return start, end


def _is_unlimited(value: int | None) -> bool:
    return value is not None and value < 0


def effective_campaign_quota(user: User | None, settings: Settings | None = None) -> int | None:
    """None = no limit."""
    settings = settings or get_settings()
    if user and user.role == "platform_admin":
        return None
    override = user.monthly_campaign_quota if user else None
    if override is not None:
        return None if _is_unlimited(override) else override
    d = settings.default_monthly_campaign_quota
    return None if _is_unlimited(d) else d


def effective_token_quota(user: User | None, settings: Settings | None = None) -> int | None:
    settings = settings or get_settings()
    if user and user.role == "platform_admin":
        return None
    override = user.monthly_token_quota if user else None
    if override is not None:
        return None if _is_unlimited(override) else override
    d = settings.default_monthly_token_quota
    return None if _is_unlimited(d) else d


def count_campaigns_this_month(db: Session, user_id: str) -> int:
    start, end = _utc_month_bounds()
    return (
        db.query(func.count(Campaign.id))
        .filter(
            Campaign.user_id == user_id,
            Campaign.created_at >= start,
            Campaign.created_at <= end,
        )
        .scalar()
        or 0
    )


def sum_tokens_this_month(db: Session, user_id: str) -> int:
    start, end = _utc_month_bounds()
    total = (
        db.query(func.coalesce(func.sum(UsageEvent.total_tokens), 0))
        .filter(
            UsageEvent.user_id == user_id,
            UsageEvent.created_at >= start,
            UsageEvent.created_at <= end,
        )
        .scalar()
    )
    return int(total or 0)


def sum_cost_usd_this_month(db: Session, user_id: str) -> Decimal:
    start, end = _utc_month_bounds()
    total = (
        db.query(func.coalesce(func.sum(UsageEvent.cost_usd), 0))
        .filter(
            UsageEvent.user_id == user_id,
            UsageEvent.created_at >= start,
            UsageEvent.created_at <= end,
        )
        .scalar()
    )
    if total is None:
        return Decimal("0")
    return Decimal(str(total))


def assert_can_create_campaign(db: Session, user: User) -> None:
    limit = effective_campaign_quota(user)
    if limit is None:
        return
    used = count_campaigns_this_month(db, user.id)
    if used >= limit:
        raise QuotaExceededError(
            f"Monthly campaign quota reached ({used}/{limit} this UTC month).",
            code="campaign_quota",
        )


def assert_can_consume_tokens(db: Session, user_id: str) -> None:
    """Block the next OpenAI call if the user is already at or over the token cap."""
    user = db.query(User).filter(User.id == user_id).first()
    limit = effective_token_quota(user)
    if limit is None:
        return
    used = sum_tokens_this_month(db, user_id)
    if used >= limit:
        raise QuotaExceededError(
            f"Monthly token quota reached ({used}/{limit} total_tokens this UTC month).",
            code="token_quota",
        )


def compute_openai_cost_usd(
    *,
    prompt_tokens: int,
    completion_tokens: int,
    settings: Settings | None = None,
) -> Decimal:
    settings = settings or get_settings()
    inp = Decimal(str(settings.openai_input_usd_per_million_tokens)) * Decimal(prompt_tokens) / Decimal(1_000_000)
    out = Decimal(str(settings.openai_output_usd_per_million_tokens)) * Decimal(completion_tokens) / Decimal(
        1_000_000
    )
    return (inp + out).quantize(Decimal("0.000001"))


def record_openai_usage(
    db: Session,
    *,
    user_id: str | None,
    campaign_id: str | None,
    model: str | None,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cost_usd: Decimal,
) -> None:
    if not user_id:
        return
    ev = UsageEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        campaign_id=campaign_id,
        provider="openai",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost_usd=cost_usd,
    )
    db.add(ev)
    db.commit()


def usage_summary_for_user(db: Session, user: User) -> dict:
    start, end = _utc_month_bounds()
    cq = effective_campaign_quota(user)
    tq = effective_token_quota(user)
    campaigns_used = count_campaigns_this_month(db, user.id)
    tokens_used = sum_tokens_this_month(db, user.id)
    cost = sum_cost_usd_this_month(db, user.id)
    return {
        "period_utc": {"start": start.isoformat(), "end": end.isoformat()},
        "campaigns": {
            "used": campaigns_used,
            "limit": cq,
            "remaining": None if cq is None else max(0, cq - campaigns_used),
        },
        "tokens": {
            "used": tokens_used,
            "limit": tq,
            "remaining": None if tq is None else max(0, tq - tokens_used),
        },
        "estimated_openai_cost_usd": str(cost),
        "quota_overrides": {
            "monthly_campaign_quota": user.monthly_campaign_quota,
            "monthly_token_quota": user.monthly_token_quota,
        },
    }
