from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Rate Limiter Gateway"
    APP_ENV: str = "dev"
    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    GIT_SHA: str = "dev"
    APP_VERSION: str = "0.1.0"

    BUCKET_CAPACITY: float = 5.0
    BUCKET_REFILL_RATE_PER_SEC: float = 1.0
    BUCKET_KEY_TTL_SEC: int = 3600
    REDIS_KEY_PREFIX: str = "bucket:"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
