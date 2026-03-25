"""
Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated config.
No secrets are hardcoded — all values must come from the environment or .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration for Sentinel Curator."""

    model_config = SettingsConfigDict(
        env_prefix="SC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_name: str = Field(default="sentinel_curator")
    db_user: str = Field(default="curator_app")
    db_password: SecretStr = Field(...)

    @property
    def db_url(self) -> str:
        """Sync SQLAlchemy connection URL (psycopg2)."""
        return (
            f"postgresql+psycopg2://{self.db_user}:"
            f"{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def async_db_url(self) -> str:
        """Async SQLAlchemy connection URL (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.db_user}:"
            f"{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # LLM
    llm_provider: Literal["openai", "azure", "local"] = Field(default="openai")
    llm_model: str = Field(default="gpt-4-turbo")
    openai_api_key: SecretStr | None = Field(default=None)
    azure_openai_endpoint: str | None = Field(default=None)
    azure_openai_api_key: SecretStr | None = Field(default=None)
    azure_openai_deployment: str | None = Field(default=None)

    # Application
    app_host: str = Field(default="127.0.0.1")
    app_port: int = Field(default=8000)
    app_env: Literal["development", "production"] = Field(default="development")
    secret_key: SecretStr = Field(...)

    # RBAC
    dev_default_role: str = Field(default="UNCLASSIFIED")

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    log_format: Literal["json", "console"] = Field(default="json")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (singleton)."""
    return Settings()  # type: ignore[call-arg]
