from __future__ import annotations

from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ethiopian Market Intelligence API"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/market_intelligence"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60

    create_tables_on_startup: bool = False
    ml_service_base_url: str = "http://localhost:8010"
    ml_request_timeout_seconds: float = 10.0
    ml_request_max_retries: int = 3
    ml_circuit_failure_threshold: int = 5
    ml_circuit_open_seconds: int = 30
    cors_allow_origins: str = "http://localhost:5173"

    @cached_property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_allow_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
