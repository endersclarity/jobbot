"""
JobBot Configuration Settings
Secure configuration management with environment variables
"""
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with secure defaults"""

    # Application settings
    PROJECT_NAME: str = "JobBot"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings - defaults to SQLite for development
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "jobbot"
    POSTGRES_PASSWORD: str = "jobbot_password"
    POSTGRES_DB: str = "jobbot"

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Email settings (for automation)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True

    # Gmail OAuth (from global CLAUDE.md)
    GMAIL_OAUTH_JSON: Optional[str] = "Gmail Oauth.json"
    GMAIL_APP_PASSWORD: Optional[str] = None

    # Scraping settings
    SCRAPING_DELAY_MIN: float = 1.0
    SCRAPING_DELAY_MAX: float = 3.0
    MAX_CONCURRENT_SCRAPERS: int = 3
    USER_AGENT_ROTATION: bool = True

    # Application limits
    MAX_DAILY_APPLICATIONS: int = 25
    MAX_FOLLOW_UPS_PER_DAY: int = 10

    # Development settings
    DEBUG: bool = False
    TESTING: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here-change-in-production":
            import secrets

            return secrets.token_urlsafe(32)
        return v

    @property
    def database_url(self) -> str:
        """Construct database URL from components"""
        # Check for DATABASE_URL environment variable first
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
            
        if not self.POSTGRES_HOST:
            # Use SQLite for development
            return "sqlite:///./jobbot.db"
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        """Async database URL for asyncpg"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
