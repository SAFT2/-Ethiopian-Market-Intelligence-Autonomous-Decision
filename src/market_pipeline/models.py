from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class RawListing:
    """Raw scraped listing before normalization."""

    source: str
    product_name: str | None
    price_text: str | None
    location_text: str | None
    date_text: str | None
    description_text: str | None
    listing_url: str | None
    raw_payload: dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class CleanListing:
    """Normalized listing ready for storage."""

    source: str
    product_name: str
    price_value: Decimal | None
    price_currency: str
    location: str | None
    listed_at: datetime | None
    description: str | None
    listing_url: str | None
    raw_payload: dict[str, Any]
    scraped_at: datetime
