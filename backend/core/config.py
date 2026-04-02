from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/core/config.py → backend dir and repo root (same layout as Docker: .env at repo root)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent

# Tier → (monthly_campaign_quota, monthly_token_quota).  -1 = unlimited.
TIER_QUOTA_MAP: dict[str, tuple[int, int]] = {
    "free": (5, 500_000),
    "professional": (50, 5_000_000),
    "growth": (200, 25_000_000),
    "enterprise": (-1, -1),
}


class Settings(BaseSettings):
    """Validated environment configuration (fail fast at startup)."""

    # Load backend/.env first, then repo root .env (later wins — matches docker-compose `env_file: .env`)
    model_config = SettingsConfigDict(
        env_file=(str(_BACKEND_DIR / ".env"), str(_REPO_ROOT / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    openai_api_key: Optional[str] = None
    mock_media_provider: Optional[str] = None
    log_level: str = "INFO"
    auth_disabled: Optional[str] = Field(default=None, validation_alias="AUTH_DISABLED")
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_default_price_id: Optional[str] = Field(default=None, validation_alias="STRIPE_DEFAULT_PRICE_ID")
    # Recurring subscription Price IDs (create in Stripe Dashboard)
    stripe_price_professional: Optional[str] = Field(default=None, validation_alias="STRIPE_PRICE_PROFESSIONAL")
    stripe_price_growth: Optional[str] = Field(default=None, validation_alias="STRIPE_PRICE_GROWTH")
    stripe_price_enterprise: Optional[str] = Field(default=None, validation_alias="STRIPE_PRICE_ENTERPRISE")
    cors_origins: Optional[str] = Field(default=None, validation_alias="CORS_ORIGINS")
    public_api_base_url: Optional[str] = Field(default=None, validation_alias="PUBLIC_API_BASE_URL")
    # Per-user defaults (User.monthly_* overrides). -1 = unlimited for that dimension.
    default_monthly_campaign_quota: int = 50
    default_monthly_token_quota: int = 5_000_000
    openai_input_usd_per_million_tokens: float = 0.15
    openai_output_usd_per_million_tokens: float = 0.60

    @property
    def cors_origin_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def mock_media_enabled(self) -> bool:
        v = self.mock_media_provider
        if v is None:
            return False
        return str(v).lower() in ("1", "true", "yes")

    @property
    def price_to_tier_map(self) -> dict[str, str]:
        """Build reverse lookup: Stripe Price ID → tier slug."""
        m: dict[str, str] = {}
        if self.stripe_price_professional:
            m[self.stripe_price_professional] = "professional"
        if self.stripe_price_growth:
            m[self.stripe_price_growth] = "growth"
        if self.stripe_price_enterprise:
            m[self.stripe_price_enterprise] = "enterprise"
        return m

    def get_tier_for_price(self, price_id: Optional[str]) -> str:
        """Resolve a Stripe Price ID to a tier slug."""
        if not price_id:
            return "free"
        # Exact match first
        tier = self.price_to_tier_map.get(price_id)
        if tier:
            return tier
        # Fallback: substring match for compatibility
        p = price_id.lower()
        if "enterprise" in p:
            return "enterprise"
        if "growth" in p:
            return "growth"
        if "professional" in p or "pro" in p:
            return "professional"
        return "free"

    def get_quotas_for_price(self, price_id: Optional[str]) -> tuple[int, int]:
        """
        Maps a Stripe Price ID to (campaign_quota, token_quota).
        Returns defaults if price_id is None or unknown.
        """
        tier = self.get_tier_for_price(price_id)
        return TIER_QUOTA_MAP.get(tier, (self.default_monthly_campaign_quota, self.default_monthly_token_quota))

    @property
    def auth_disabled_flag(self) -> bool:
        v = self.auth_disabled
        if v is None:
            return False
        return str(v).lower() in ("1", "true", "yes")


@lru_cache
def get_settings() -> Settings:
    return Settings()
