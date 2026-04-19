from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import Response

from market_pipeline.config import Settings
from market_pipeline.models import RawListing
from market_pipeline.scrapers.base import BaseScraper


LOGGER = logging.getLogger(__name__)


class JijiEthiopiaScraper(BaseScraper):
    """Scraper for Jiji Ethiopia listing pages."""

    BASE_URL = "https://jiji.com.et"

    def __init__(self, settings: Settings, category_path: str = "/all") -> None:
        self.settings = settings
        self.category_path = category_path
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    def scrape(self) -> list[RawListing]:
        listings: list[RawListing] = []

        for page in range(1, self.settings.max_pages + 1):
            url = f"{self.BASE_URL}{self.category_path}?page={page}"
            LOGGER.info("Scraping page %s", url)
            try:
                page_html = self._fetch_with_retries(url)
                if page_html is None:
                    continue

                page_listings = self._parse_listing_page(page_html)
                LOGGER.info("Found %d listings on page %d", len(page_listings), page)
                listings.extend(page_listings)
            except Exception:
                LOGGER.exception("Unexpected error scraping page %s", url)

            time.sleep(self.settings.sleep_seconds_between_requests)

        return listings

    def _fetch_with_retries(self, url: str) -> str | None:
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                response = self.session.get(
                    url,
                    timeout=self.settings.request_timeout_seconds,
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                LOGGER.warning(
                    "Request failed for %s (attempt %d/%d): %s",
                    url,
                    attempt,
                    self.settings.max_retries,
                    exc,
                )
                if attempt == self.settings.max_retries:
                    LOGGER.error("Exhausted retries for %s", url)
                    return None
                time.sleep(0.8 * attempt)
        return None

    def _parse_listing_page(self, html: str) -> list[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        # Multiple selectors improve resilience when the source changes classes.
        cards = soup.select("div.b-list-advert__item") or soup.select("article")

        listings: list[RawListing] = []
        for card in cards:
            parsed = self._parse_card(card)
            if parsed is not None:
                listings.append(parsed)

        return listings

    def _parse_card(self, card: Any) -> RawListing | None:
        product_name = self._safe_text(
            card.select_one(".qa-advert-title")
            or card.select_one("h4")
            or card.select_one("h3")
            or card.select_one("a")
        )
        price_text = self._safe_text(
            card.select_one(".qa-advert-price")
            or card.select_one("[class*='price']")
        )

        location_text = self._safe_text(
            card.select_one(".b-list-advert-base__item-location")
            or card.select_one("[class*='location']")
        )
        date_text = self._safe_text(
            card.select_one(".b-list-advert-base__item-time")
            or card.select_one("time")
            or card.select_one("[class*='date']")
        )

        link_tag = card.select_one("a[href]")
        listing_url = None
        if link_tag and link_tag.get("href"):
            listing_url = urljoin(self.BASE_URL, str(link_tag["href"]))

        description_text = self._extract_inline_description(card)

        if description_text is None and listing_url is not None:
            description_text = self._fetch_description_from_detail_page(listing_url)

        payload = {
            "product_name": product_name,
            "price_text": price_text,
            "location_text": location_text,
            "date_text": date_text,
            "description_text": description_text,
            "listing_url": listing_url,
        }

        if not product_name and not price_text:
            return None

        return RawListing(
            source="jiji_ethiopia",
            product_name=product_name,
            price_text=price_text,
            location_text=location_text,
            date_text=date_text,
            description_text=description_text,
            listing_url=listing_url,
            raw_payload=payload,
            scraped_at=datetime.utcnow(),
        )

    def _fetch_description_from_detail_page(self, url: str) -> str | None:
        detail_html = self._fetch_with_retries(url)
        if detail_html is None:
            return None

        soup = BeautifulSoup(detail_html, "html.parser")
        candidates = [
            soup.select_one("div.b-advert-description__content"),
            soup.select_one("div.qa-advert-description"),
            soup.select_one("[class*='description']"),
        ]

        for item in candidates:
            text = self._safe_text(item)
            if text:
                return text
        return None

    @staticmethod
    def _extract_inline_description(card: Any) -> str | None:
        return JijiEthiopiaScraper._safe_text(
            card.select_one(".b-list-advert-base__description-text")
            or card.select_one("[class*='description']")
        )

    @staticmethod
    def _safe_text(node: Any) -> str | None:
        if node is None:
            return None
        text = " ".join(node.get_text(" ", strip=True).split())
        return text or None
