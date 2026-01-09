"""Application settings configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SRCEI credentials (required)
    srcei_rut: str = Field(..., description="Chilean RUT with dash (e.g., 12345678-9)")
    srcei_password: str = Field(..., description="SRCEI account password")
    srcei_username: str = Field(..., description="SRCEI username (usually same as RUT)")

    # Server configuration (optional)
    port: int = Field(default=8080, description="Server port")
    environment: str = Field(default="production", description="Environment name")


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
