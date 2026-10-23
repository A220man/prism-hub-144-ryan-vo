# Backend Configuration
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Prism Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./prism_hub.db"

    # OIDC / Keycloak
    OIDC_ISSUER_URL: str = "http://127.0.0.1:8080/realms/prism-hub"
    OIDC_CLIENT_ID: str = "prism-hub-backend"
    OIDC_CLIENT_SECRET: str = ""
    OIDC_AUDIENCE: str = "prism-hub-api"

    # LLM
    LLM_PROVIDER: str = "openai-compatible"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_BASE_URL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]

    # Demo mode (explicitly enabled, refuses in production)
    DEMO_MODE: bool = False

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def validate_demo_mode(self) -> None:
        if self.DEMO_MODE and self.is_production:
            raise RuntimeError("DEMO_MODE is not allowed in production")


@lru_cache()
def get_settings() -> Settings:
    return Settings()