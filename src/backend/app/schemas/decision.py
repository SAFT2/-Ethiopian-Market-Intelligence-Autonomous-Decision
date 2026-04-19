from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DecisionCreate(BaseModel):
    product_id: int = Field(gt=0)
    prediction_id: int | None = Field(default=None, gt=0)
    decision_type: str = Field(min_length=3, max_length=60)
    recommendation: dict
    risk_score: Decimal = Field(ge=0, le=1)
    status: str = Field(min_length=3, max_length=20)


class DecisionResponse(DecisionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
