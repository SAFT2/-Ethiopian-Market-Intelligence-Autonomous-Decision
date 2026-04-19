from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    database_url: str
    user_agent: str
    request_timeout_seconds: int = 20
    max_pages: int = 3
    max_retries: int = 3
    sleep_seconds_between_requests: float = 1.0


def load_settings() -> Settings:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/market_intelligence",
    )
    user_agent = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    )

    return Settings(
        database_url=database_url,
        user_agent=user_agent,
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20")),
        max_pages=int(os.getenv("JIJI_MAX_PAGES", "3")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        sleep_seconds_between_requests=float(
            os.getenv("SLEEP_SECONDS_BETWEEN_REQUESTS", "1.0")
        ),
    )
