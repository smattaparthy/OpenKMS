from typing import Optional
from functools import lru_cache

try:
    # Pydantic 2.x - BaseSettings moved to pydantic-settings
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost/openkms",
        env="DATABASE_URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS
    FRONTEND_URL: str = Field(default="http://localhost:5000", env="FRONTEND_URL")

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OpenKMS"

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()