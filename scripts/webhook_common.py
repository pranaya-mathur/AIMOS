"""Shared HMAC signing helpers for media webhook tests."""

import hashlib
import hmac
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Single source of truth (same headers the API verifies)
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "backend"))

from services.integrations.webhook_constants import PROVIDER_SIGNATURE_HEADERS  # noqa: E402


def build_signature(secret: str, raw_body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def post_signed_webhook(
    *,
    base_url: str,
    provider: str,
    secret: str,
    payload: dict,
    timeout_sec: float = 30.0,
) -> tuple[int, str]:
    raw = json.dumps(payload).encode("utf-8")
    signature = build_signature(secret, raw)
    sig_header = PROVIDER_SIGNATURE_HEADERS[provider]
    endpoint = f"{base_url.rstrip('/')}/media/webhook/{provider}"
    req = urllib.request.Request(
        endpoint,
        data=raw,
        headers={
            "content-type": "application/json",
            sig_header: signature,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
