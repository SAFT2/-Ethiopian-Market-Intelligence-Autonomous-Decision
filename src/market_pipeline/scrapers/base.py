from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from market_pipeline.models import RawListing


class BaseScraper(ABC):
    """Base interface for all marketplace scrapers."""

    @abstractmethod
    def scrape(self) -> Iterable[RawListing]:
        """Yield raw listings from the source."""
