from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.prediction import PredictionCreate, PredictionResponse
from app.services.predictions_service import PredictionsService


router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    payload: PredictionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
) -> PredictionResponse:
    item = PredictionsService(db).create(payload)
    return PredictionResponse.model_validate(item)


@router.get("", response_model=list[PredictionResponse])
def list_predictions(
    product_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> list[PredictionResponse]:
    items = PredictionsService(db).list(product_id=product_id, limit=limit)
    return [PredictionResponse.model_validate(i) for i in items]
