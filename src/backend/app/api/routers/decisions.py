from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.decision import DecisionCreate, DecisionResponse
from app.services.decisions_service import DecisionsService


router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
def create_decision(
    payload: DecisionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
) -> DecisionResponse:
    item = DecisionsService(db).create(payload)
    return DecisionResponse.model_validate(item)


@router.get("", response_model=list[DecisionResponse])
def list_decisions(
    product_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> list[DecisionResponse]:
    items = DecisionsService(db).list(product_id=product_id, limit=limit)
    return [DecisionResponse.model_validate(i) for i in items]
