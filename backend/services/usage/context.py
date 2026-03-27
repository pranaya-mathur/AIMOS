from __future__ import annotations

from contextvars import ContextVar
from typing import Any

_ctx: ContextVar[dict[str, Any] | None] = ContextVar("aimos_usage_ctx", default=None)


def set_usage_context(*, user_id: str | None, campaign_id: str | None = None) -> None:
    _ctx.set({"user_id": user_id, "campaign_id": campaign_id})


def clear_usage_context() -> None:
    _ctx.set(None)


def get_usage_context() -> dict[str, Any] | None:
    return _ctx.get()
