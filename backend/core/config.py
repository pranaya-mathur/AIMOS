from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/core/config.py → backend dir and repo root (same layout as Docker: .env at repo root)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_DIR.parent

# Tier → (monthly_campaign_quota, monthly_token_quota, max_media_jobs). -1 = unlimited.
TIER_QUOTA_MAP: dict[str, tuple[int, int, int]] = {
    "free": (5, 500_000, 2),
    "professional": (50, 5_000_000, 10),
    "growth": (200, 25_000_000, 50),
    "enterprise": (-1, -1, -1),
}

# Hardened 2.0 Lean & Tiered Pivot (AIM-250)
_FREE_AGENTS = ["competitive_spy", "business_analyzer", "brand_builder", "business_dashboard"]
_PRO_AGENTS = _FREE_AGENTS + ["content_studio", "predictive_benchmarker", "campaign_builder", "social_media_manager"]
_GROWTH_AGENTS = _PRO_AGENTS + ["lead_capture", "sales_agent", "customer_engagement", "performance_brain", "growth_planner"]

TIER_AGENT_PERMISSIONS: dict[str, list[str]] = {
    "free": _FREE_AGENTS,
    "professional": _PRO_AGENTS,
    "growth": _GROWTH_AGENTS,
    "enterprise": _GROWTH_AGENTS + ["wisdom_extractor"]
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
    # Dev only: include `reset_token` in POST /auth/password-reset/request JSON (no email is sent).
    password_reset_token_in_response: bool = Field(
        default=False,
        validation_alias="PASSWORD_RESET_TOKEN_IN_RESPONSE",
    )
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
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
    stability_api_key: Optional[str] = Field(default=None, validation_alias="STABILITY_API_KEY")
    
    # Sovereign Mode (Phase 2: GGUF Creative Engine)
    sovereign_mode: bool = Field(default=False, validation_alias="SOVEREIGN_MODE")
    sd_model_path: str = Field(default="backend/models/sovereign/flux1-dev-q6_k.gguf", validation_alias="SD_MODEL_PATH")
    sd_n_threads: int = Field(default=4, validation_alias="SD_N_THREADS")
    inference_quality_floor: str = Field(default="q6_k", validation_alias="INFERENCE_QUALITY_FLOOR")
    
    memory_guard_enabled: bool = Field(default=True, validation_alias="MEMORY_GUARD_ENABLED")
    memory_threshold_gb: float = Field(default=12.0, validation_alias="MEMORY_THRESHOLD_GB")
    # Per-user defaults (User.monthly_* overrides). -1 = unlimited for that dimension.
    default_monthly_campaign_quota: int = 50
    default_monthly_token_quota: int = 5_000_000
    openai_input_usd_per_million_tokens: float = 0.15
    openai_output_usd_per_million_tokens: float = 0.60
    sentry_dsn: Optional[str] = Field(default=None, validation_alias="SENTRY_DSN")

    @property
    def cors_origin_list(self) -> list[str]:
        """Browser calls from Next (localhost:3000) to API (localhost:8000) require CORS."""
        raw = [o.strip() for o in (self.cors_origins or "").split(",") if o.strip()]
        if raw:
            return raw
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://[::1]:3000",
        ]

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

    def get_quotas_for_price(self, price_id: Optional[str]) -> tuple[int, int, int]:
        """
        Maps a Stripe Price ID to (campaign_quota, token_quota, max_media_jobs).
        Returns defaults if price_id is None or unknown.
        """
        tier = self.get_tier_for_price(price_id)
        # Default to Professional if free or unknown for safety
        return TIER_QUOTA_MAP.get(tier, (50, 5_000_000, 10))

    @property
    def auth_disabled_flag(self) -> bool:
        v = self.auth_disabled
        if v is None:
            return False
        return str(v).lower() in ("1", "true", "yes")


@lru_cache
def get_settings() -> Settings:
    return Settings()
