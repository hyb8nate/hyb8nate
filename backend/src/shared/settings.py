"""Settings Module."""

import uuid
from enum import Enum

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Labels(BaseModel):
    """Labels Model."""

    NAMESPACE_LABEL_KEY: str = "hyb8nate.xyz/enabled"
    NAMESPACE_LABEL_VALUE: str = "true"


class Environment(str, Enum):
    """ENUM Environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    PREPRODUCTION = "preproduction"
    STAGING = "staging"


class LogLevel(str, Enum):
    """ENUM LogLevel."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(Labels, BaseSettings):
    """API settings."""

    # ENV
    PORT: int = 8000
    ENVIRONMENT: Environment = Environment.PRODUCTION
    LOG_LEVEL: LogLevel = LogLevel.ERROR
    DEBUG: bool = False
    TIMEZONE: str = "Europe/Paris"

    # AUTH
    ADMIN_PASSWORD: str = "admin"  # Change via ADMIN_PASSWORD env var
    JWT_SECRET_KEY: str = str(uuid.uuid4())
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        # .env.prod takes priority over `.env`
        env_file=(".env", ".env.prod"),
        extra="ignore",
    )


settings = Settings()
