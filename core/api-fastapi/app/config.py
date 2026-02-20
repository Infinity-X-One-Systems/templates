"""Application configuration via environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Service identity
    SERVICE_NAME: str = "infinity-api"
    API_VERSION: str = "1.0.0"
    ENV: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    # Security
    SECRET_KEY: str = "change-me-in-production-use-256-bit-random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://infinityxai.com", "https://vizual-x.com"]

    # Database (optional – override in composed systems)
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" | "text"

    # Telemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    OTEL_SAMPLING_RATIO: float = 1.0

    # Memory interface
    MEMORY_BACKEND: str = "in-memory"  # "in-memory" | "redis" | "postgres"
    MEMORY_TTL_SECONDS: int = 3600

    @field_validator("ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
