from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Optional, Union

_ctx: ContextVar[Optional[dict[str, Any]]] = ContextVar("aimos_usage_ctx", default=None)


def set_usage_context(*, user_id: Optional[str], campaign_id: Optional[str] = None) -> None:
    _ctx.set({"user_id": user_id, "campaign_id": campaign_id})


def clear_usage_context() -> None:
    _ctx.set(None)


def get_usage_context() -> Optional[dict[str, Any]]:
    return _ctx.get()
