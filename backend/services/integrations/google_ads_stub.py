"""
Google Ads API — production setup uses the official `google-ads` client + OAuth.

This module only validates intent and returns a structured placeholder so the
HTTP layer can stay consistent until credentials + developer token are configured.

Docs: https://developers.google.com/google-ads/api/docs/start
"""

from __future__ import annotations

import os
from typing import Optional


class GoogleAdsNotConfiguredError(RuntimeError):
    pass


def enqueue_google_ads_placeholder(*, campaign_name: str, customer_id: Optional[str] = None) -> dict:
    cid = customer_id or os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    dev = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not cid or not dev:
        raise GoogleAdsNotConfiguredError(
            "Set GOOGLE_ADS_CUSTOMER_ID and GOOGLE_ADS_DEVELOPER_TOKEN; "
            "then integrate google-ads Python library for real campaign creation."
        )
    return {
        "provider": "google_ads",
        "status": "not_implemented",
        "message": "Wire google-ads library + OAuth; credentials detected but RPC not executed in this build.",
        "campaign_name": campaign_name,
        "customer_id": cid,
    }
