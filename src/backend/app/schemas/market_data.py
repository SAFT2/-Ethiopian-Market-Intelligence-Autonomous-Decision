from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MarketDataCreate(BaseModel):
    product_id: int = Field(gt=0)
    product_name: str = Field(min_length=2, max_length=255)
    price_value: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="ETB", min_length=3, max_length=10)
    location: str | None = Field(default=None, max_length=255)
    observed_at: datetime
    source: str = Field(min_length=2, max_length=80)
    listing_url: str | None = None
    description: str | None = None


class MarketDataResponse(MarketDataCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
