from __future__ import annotations

import logging
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation

from market_pipeline.models import CleanListing, RawListing


LOGGER = logging.getLogger(__name__)

CURRENCY_PATTERN = re.compile(r"(etb|birr|br)", re.IGNORECASE)
NUMBER_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")


def normalize_listing(raw: RawListing) -> CleanListing | None:
    """Convert a raw listing into standardized structure."""

    product_name = _normalize_text(raw.product_name)
    if not product_name:
        LOGGER.warning("Dropping listing with missing product name: %s", raw.raw_payload)
        return None

    price_value, price_currency = _normalize_price(raw.price_text)
    location = _normalize_location(raw.location_text)
    listed_at = _normalize_date(raw.date_text)
    description = _normalize_text(raw.description_text)

    return CleanListing(
        source=raw.source,
        product_name=product_name,
        price_value=price_value,
        price_currency=price_currency,
        location=location,
        listed_at=listed_at,
        description=description,
        listing_url=raw.listing_url,
        raw_payload=raw.raw_payload,
        scraped_at=raw.scraped_at,
    )


def normalize_batch(raw_listings: list[RawListing]) -> list[CleanListing]:
    normalized: list[CleanListing] = []
    for raw in raw_listings:
        try:
            item = normalize_listing(raw)
            if item is not None:
                normalized.append(item)
        except Exception:
            LOGGER.exception("Error normalizing listing: %s", raw.raw_payload)
    return normalized


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.split())
    return cleaned.strip() or None


def _normalize_location(location_text: str | None) -> str | None:
    value = _normalize_text(location_text)
    if value is None:
        return None

    value = value.replace("Addis Abeba", "Addis Ababa")
    return value.title()


def _normalize_price(price_text: str | None) -> tuple[Decimal | None, str]:
    if not price_text:
        return None, "ETB"

    lowered = price_text.lower()
    currency = "ETB" if CURRENCY_PATTERN.search(lowered) else "ETB"

    parts = NUMBER_PATTERN.findall(price_text.replace(",", ""))
    if not parts:
        return None, currency

    # For ranges we store the first numeric value as canonical scalar.
    numeric_text = parts[0].replace(",", "")
    try:
        value = Decimal(numeric_text)
    except InvalidOperation:
        return None, currency

    return value, currency


def _normalize_date(date_text: str | None) -> datetime | None:
    if not date_text:
        return None

    value = date_text.strip().lower()
    now = datetime.now(UTC)

    if "today" in value:
        return now
    if "yesterday" in value:
        return now - timedelta(days=1)

    days_match = re.search(r"(\d+)\s+day", value)
    if days_match:
        return now - timedelta(days=int(days_match.group(1)))

    hours_match = re.search(r"(\d+)\s+hour", value)
    if hours_match:
        return now - timedelta(hours=int(hours_match.group(1)))

    # Attempt multiple date formats commonly seen in listing platforms.
    date_formats = [
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%Y-%m-%d",
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(date_text.strip(), fmt)
            return parsed.replace(tzinfo=UTC)
        except ValueError:
            continue

    LOGGER.debug("Unable to parse listing date: %s", date_text)
    return None
