"""
Meta Marketing API — draft campaign creation (Graph API).

Requires: META_ACCESS_TOKEN, META_AD_ACCOUNT_ID (digits or act_xxx).
See: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign
"""

from __future__ import annotations

import os

import httpx

GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v21.0")


class MetaMarketingError(RuntimeError):
    pass


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise MetaMarketingError(f"{name} is not set")
    return v


def create_draft_campaign_on_meta(
    *,
    name: str,
    objective: str = "OUTCOME_AWARENESS",
    status: str = "PAUSED",
) -> dict:
    """Creates a PAUSED campaign in the ad account (safe default)."""
    token = _require_env("META_ACCESS_TOKEN")
    raw_acct = _require_env("META_AD_ACCOUNT_ID").replace("act_", "")
    act = f"act_{raw_acct}"

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{act}/campaigns"
    body = {
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": [],
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, params={"access_token": token}, json=body)
        data = resp.json()
    if resp.status_code >= 400:
        raise MetaMarketingError(str(data))
    return {"provider": "meta", "raw": data}
