from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.decision import Decision
from app.schemas.decision import DecisionCreate


class DecisionsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: DecisionCreate) -> Decision:
        item = Decision(
            product_id=payload.product_id,
            prediction_id=payload.prediction_id,
            decision_type=payload.decision_type,
            recommendation=payload.recommendation,
            risk_score=payload.risk_score,
            status=payload.status,
            created_at=datetime.now(UTC),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, product_id: int | None = None, limit: int = 100) -> list[Decision]:
        query = self.db.query(Decision)
        if product_id is not None:
            query = query.filter(Decision.product_id == product_id)
        return query.order_by(Decision.created_at.desc()).limit(limit).all()
