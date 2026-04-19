from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DemandTrainRequest(BaseModel):
    csv_path: str


class ProductScoringTrainRequest(BaseModel):
    csv_path: str


class AnomalyTrainRequest(BaseModel):
    csv_path: str


class TrainResponse(BaseModel):
    model_name: str
    model_version: str
    metrics: dict


class DemandPredictRequest(BaseModel):
    product_id: int = Field(gt=0)
    location: str
    history_prices: list[float] = Field(min_length=3)


class ProductScorePredictRequest(BaseModel):
    avg_monthly_sales: float = Field(ge=0)
    avg_margin_pct: float = Field(ge=0, le=1)
    demand_growth_pct: float = Field(ge=-1, le=3)
    stockout_rate: float = Field(ge=0, le=1)
    market_volatility: float = Field(ge=0)


class AnomalyPredictRequest(BaseModel):
    recent_prices: list[float] = Field(min_length=3)


class PredictResponse(BaseModel):
    model_name: str
    model_version: str
    prediction: float
    metadata: dict
    predicted_at: datetime
