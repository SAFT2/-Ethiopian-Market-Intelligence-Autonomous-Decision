from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate


class PredictionsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: PredictionCreate) -> Prediction:
        item = Prediction(
            product_id=payload.product_id,
            model_name=payload.model_name,
            horizon_days=payload.horizon_days,
            predicted_price=payload.predicted_price,
            confidence=payload.confidence,
            predicted_for=payload.predicted_for,
            created_at=datetime.now(UTC),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, product_id: int | None = None, limit: int = 100) -> list[Prediction]:
        query = self.db.query(Prediction)
        if product_id is not None:
            query = query.filter(Prediction.product_id == product_id)
        return query.order_by(Prediction.predicted_for.desc()).limit(limit).all()
