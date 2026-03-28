"""
WhatsApp Cloud API — send a text message.

Requires: WHATSAPP_CLOUD_TOKEN, WHATSAPP_PHONE_NUMBER_ID
See: https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages
"""

from __future__ import annotations

import os

import httpx

GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v21.0")


class WhatsAppCloudError(RuntimeError):
    pass


def _require_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise WhatsAppCloudError(f"{name} is not set")
    return v


def send_text_message(*, to_e164: str, body: str) -> dict:
    """Send plain text (user must have opted in / thread rules apply)."""
    if os.getenv("MOCK_WHATSAPP") == "1":
        import logging
        logging.getLogger(__name__).info("[MOCK WHATSAPP] To: %s, Body: %s", to_e164, body)
        return {"provider": "whatsapp", "mock": True, "raw": {"message_id": "mock_id"}}

    token = _require_env("WHATSAPP_CLOUD_TOKEN")
    phone_id = _require_env("WHATSAPP_PHONE_NUMBER_ID")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_e164,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        data = resp.json() if resp.content else {}
    if resp.status_code >= 400:
        raise WhatsAppCloudError(str(data))
    return {"provider": "whatsapp", "raw": data}
