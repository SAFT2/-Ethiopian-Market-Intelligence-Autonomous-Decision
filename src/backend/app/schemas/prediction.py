from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PredictionCreate(BaseModel):
    product_id: int = Field(gt=0)
    model_name: str = Field(min_length=2, max_length=120)
    horizon_days: int = Field(gt=0, le=365)
    predicted_price: Decimal = Field(ge=0)
    confidence: Decimal | None = Field(default=None, ge=0, le=1)
    predicted_for: datetime


class PredictionResponse(PredictionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
