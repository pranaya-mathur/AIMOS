from calendar import monthrange
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import get_settings
from db import get_db
from deps import get_current_user_optional
from models import User
from services.usage.quotas import usage_summary_for_user

router = APIRouter()


@router.get("/me")
def my_usage(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    """Monthly campaign + OpenAI token usage, estimated cost, and effective quota limits."""
    settings = get_settings()
    if user is None:
        if settings.auth_disabled_flag:
            now = datetime.now(timezone.utc)
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last = monthrange(now.year, now.month)[1]
            end = now.replace(
                day=last, hour=23, minute=59, second=59, microsecond=999999
            )
            return {
                "period_utc": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                "campaigns": {"used": 0, "limit": None, "remaining": None},
                "tokens": {"used": 0, "limit": None, "remaining": None},
                "estimated_openai_cost_usd": "0",
                "quota_overrides": {
                    "monthly_campaign_quota": None,
                    "monthly_token_quota": None,
                },
                "note": "AUTH_DISABLED: sign in for per-user quota usage.",
            }
        raise HTTPException(status_code=401, detail="Not authenticated")
    return usage_summary_for_user(db, user)
