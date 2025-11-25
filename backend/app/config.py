from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import os


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/binko"
    openai_api_key: str = ""
    
    # Production settings
    environment: str = "development"  # development, staging, production
    cors_origins: str = "*"  # Comma-separated list
    log_level: str = "INFO"
    
    # Rate limiting (placeholder for future)
    rate_limit_per_minute: int = 60

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str, info) -> str:
        """Warn if OpenAI key missing in production."""
        env = info.data.get("environment", "development")
        if env == "production" and not v:
            raise ValueError("openai_api_key required in production")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL starts with postgresql."""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("database_url must be PostgreSQL connection string")
        return v

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
