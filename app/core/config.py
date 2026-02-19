from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Rate Limiter Gateway"
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    GIT_SHA: str = "dev"
    APP_VERSION: str = "0.1.0"

    # Dependencies
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_KEY_PREFIX: str = "bucket:"

    # Token bucket defaults (validated)
    BUCKET_CAPACITY: Annotated[float, Field(gt=0)] = 5.0
    BUCKET_REFILL_RATE_PER_SEC: Annotated[float, Field(gt=0)] = 1.0
    BUCKET_KEY_TTL_SEC: Annotated[int, Field(ge=0)] = 3600

    # Gateway guardrails
    MAX_BODY_BYTES: Annotated[int, Field(ge=0)] = 32768

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
