"""Which external integrations have env configured (no secret values returned)."""

import os


def snapshot() -> dict:
    return {
        "meta_marketing": bool(os.getenv("META_ACCESS_TOKEN") and os.getenv("META_AD_ACCOUNT_ID")),
        "whatsapp_cloud": bool(os.getenv("WHATSAPP_CLOUD_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID")),
        "google_ads_env": bool(os.getenv("GOOGLE_ADS_CUSTOMER_ID") and os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")),
        "stripe": bool(os.getenv("STRIPE_SECRET_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "adcreative": bool(os.getenv("ADCREATIVE_API_KEY")),
        "pictory": bool(os.getenv("PICTORY_API_KEY")),
        "elevenlabs": bool(os.getenv("ELEVENLABS_API_KEY")),
    }
