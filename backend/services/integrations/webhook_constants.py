"""
Single source of truth for media webhook signing (backend + scripts must match).

Scripts add `backend/` to PYTHONPATH and import from here to avoid drift.
"""

from typing import Final

PROVIDER_SIGNATURE_HEADERS: Final[dict[str, str]] = {
    "adcreative": "x-adcreative-signature",
    "pictory": "x-pictory-signature",
    "elevenlabs": "x-elevenlabs-signature",
}

PROVIDER_WEBHOOK_SECRET_ENV: Final[dict[str, str]] = {
    "adcreative": "ADCREATIVE_WEBHOOK_SECRET",
    "pictory": "PICTORY_WEBHOOK_SECRET",
    "elevenlabs": "ELEVENLABS_WEBHOOK_SECRET",
}

SUPPORTED_MEDIA_PROVIDERS: Final[frozenset[str]] = frozenset(PROVIDER_SIGNATURE_HEADERS.keys())
