from __future__ import annotations

import logging

from market_pipeline.cleaning.normalizer import normalize_batch
from market_pipeline.config import load_settings
from market_pipeline.logging_utils import configure_logging
from market_pipeline.scrapers.jiji_ethiopia import JijiEthiopiaScraper
from market_pipeline.storage.db import build_session_factory, create_tables
from market_pipeline.storage.repository import ListingRepository


LOGGER = logging.getLogger(__name__)


def run() -> None:
    configure_logging()
    settings = load_settings()

    LOGGER.info("Starting market pipeline")

    create_tables(settings.database_url)
    session_factory = build_session_factory(settings.database_url)

    scraper = JijiEthiopiaScraper(settings=settings)
    raw_listings = scraper.scrape()
    LOGGER.info("Scraped %d raw listings", len(raw_listings))

    clean_listings = normalize_batch(raw_listings)
    LOGGER.info("Normalized %d listings", len(clean_listings))

    with session_factory() as session:
        repository = ListingRepository(session)
        inserted_count = repository.upsert_many(clean_listings)
        session.commit()

    LOGGER.info("Pipeline completed. Rows written: %d", inserted_count)


if __name__ == "__main__":
    run()
