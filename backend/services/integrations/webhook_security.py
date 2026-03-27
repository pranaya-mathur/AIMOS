import hashlib
import hmac
import os

from services.integrations.webhook_constants import (
    PROVIDER_SIGNATURE_HEADERS,
    PROVIDER_WEBHOOK_SECRET_ENV,
)


def _expected_signature(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def verify_provider_signature(provider: str, body: bytes, headers: dict):
    provider = provider.lower()
    if provider not in PROVIDER_SIGNATURE_HEADERS:
        return False, "Unsupported provider"

    secret_env_key = PROVIDER_WEBHOOK_SECRET_ENV[provider]
    secret = os.getenv(secret_env_key)
    if not secret:
        return False, f"Missing {secret_env_key}"

    signature_header = PROVIDER_SIGNATURE_HEADERS[provider]
    provided_signature = headers.get(signature_header)
    if not provided_signature:
        return False, f"Missing {signature_header}"

    expected = _expected_signature(secret, body)
    if not hmac.compare_digest(provided_signature, expected):
        return False, "Invalid signature"
    return True, "ok"


# Back-compat for imports expecting old names
PROVIDER_SIG_HEADERS = PROVIDER_SIGNATURE_HEADERS
PROVIDER_SECRET_ENV = PROVIDER_WEBHOOK_SECRET_ENV
