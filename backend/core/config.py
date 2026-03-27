from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated environment configuration (fail fast at startup)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
    cors_origins: Optional[str] = Field(default=None, validation_alias="CORS_ORIGINS")
    public_api_base_url: Optional[str] = Field(default=None, validation_alias="PUBLIC_API_BASE_URL")

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
    def auth_disabled_flag(self) -> bool:
        v = self.auth_disabled
        if v is None:
            return False
        return str(v).lower() in ("1", "true", "yes")


@lru_cache
def get_settings() -> Settings:
    return Settings()
