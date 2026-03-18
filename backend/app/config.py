"""Application configuration via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://cybersec:password@localhost:5432/cybersec"

    # Security
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Microsoft 365 / Azure AD
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None
    microsoft_redirect_uri: str = "http://localhost:8000/api/integrations/microsoft/callback"

    # Google Workspace
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/integrations/google/callback"

    # App
    frontend_url: str = "http://localhost:3000"
    sync_interval_minutes: int = 30
    environment: str = "development"
    log_level: str = "INFO"

    # Encryption key for storing OAuth tokens (Fernet key, base64)
    encryption_key: Optional[str] = None

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def microsoft_configured(self) -> bool:
        return bool(self.microsoft_client_id and self.microsoft_client_secret)

    @property
    def google_configured(self) -> bool:
        return bool(self.google_client_id and self.google_client_secret)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
