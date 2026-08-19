from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "JobPulse"
    debug: bool = False
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/jobpulse"
    primary_source: str = "jobicy"
    fallback_source: str = "sandbox"
    ingestion_interval_minutes: int = 30
    requests_per_minute: int = 30
    min_request_interval_seconds: float = 2.0
    max_retries: int = 3
    backoff_base_seconds: float = 1.0
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_cooldown_seconds: int = 60
    frontend_origin: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "dev-secret-key"
    sandbox_scenario: str = "normal"
    source_status_check_interval_seconds: int = 30

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
