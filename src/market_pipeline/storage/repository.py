from __future__ import annotations

import logging
from collections.abc import Sequence

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from market_pipeline.models import CleanListing
from market_pipeline.storage.db import MarketListingRecord
from market_pipeline.utils import stable_hash


LOGGER = logging.getLogger(__name__)


class ListingRepository:
    """Database access methods for cleaned market listings."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_many(self, listings: Sequence[CleanListing]) -> int:
        if not listings:
            return 0

        rows = []
        for listing in listings:
            payload = {
                "source": listing.source,
                "product_name": listing.product_name,
                "price_value": listing.price_value,
                "price_currency": listing.price_currency,
                "location": listing.location,
                "listed_at": listing.listed_at,
                "description": listing.description,
                "listing_url": listing.listing_url,
                "raw_payload": listing.raw_payload,
                "scraped_at": listing.scraped_at,
            }
            payload["unique_hash"] = stable_hash(payload)
            rows.append(payload)

        stmt = insert(MarketListingRecord).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[MarketListingRecord.unique_hash],
            set_={
                "product_name": stmt.excluded.product_name,
                "price_value": stmt.excluded.price_value,
                "price_currency": stmt.excluded.price_currency,
                "location": stmt.excluded.location,
                "listed_at": stmt.excluded.listed_at,
                "description": stmt.excluded.description,
                "listing_url": stmt.excluded.listing_url,
                "raw_payload": stmt.excluded.raw_payload,
                "scraped_at": stmt.excluded.scraped_at,
            },
        )

        result = self.session.execute(stmt)
        LOGGER.info("Upserted %d rows", result.rowcount or 0)
        return result.rowcount or 0
