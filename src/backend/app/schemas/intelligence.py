from __future__ import annotations

from pydantic import BaseModel, Field


class IntelligenceRequest(BaseModel):
    product_id: int = Field(gt=0)
    location: str
    current_price: float = Field(gt=0)
    avg_market_price: float = Field(gt=0)
    inventory_days_cover: float = Field(ge=0)
    weekly_sales_units: float = Field(ge=0)
    history_prices: list[float] = Field(min_length=3)


class IntelligenceResponse(BaseModel):
    product_id: int
    demand_forecast: float
    product_score: float
    anomaly_probability: float
    pricing_recommendation: str
    stock_decision: str
    risk_alert: str
    score: float
    explanation: list[str]
