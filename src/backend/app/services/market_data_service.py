from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.market_data import MarketDataPoint
from app.schemas.market_data import MarketDataCreate


class MarketDataService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: MarketDataCreate) -> MarketDataPoint:
        point = MarketDataPoint(
            product_id=payload.product_id,
            product_name=payload.product_name,
            price_value=payload.price_value,
            currency=payload.currency,
            location=payload.location,
            observed_at=payload.observed_at,
            source=payload.source,
            listing_url=payload.listing_url,
            description=payload.description,
            created_at=datetime.now(UTC),
        )
        self.db.add(point)
        self.db.commit()
        self.db.refresh(point)
        return point

    def list(self, product_id: int | None = None, limit: int = 100) -> list[MarketDataPoint]:
        query = self.db.query(MarketDataPoint)
        if product_id is not None:
            query = query.filter(MarketDataPoint.product_id == product_id)
        return query.order_by(MarketDataPoint.observed_at.desc()).limit(limit).all()
