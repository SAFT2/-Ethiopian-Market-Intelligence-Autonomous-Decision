from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.market_data import MarketDataCreate, MarketDataResponse
from app.services.market_data_service import MarketDataService


router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.post("", response_model=MarketDataResponse, status_code=status.HTTP_201_CREATED)
def create_market_data(
    payload: MarketDataCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
) -> MarketDataResponse:
    item = MarketDataService(db).create(payload)
    return MarketDataResponse.model_validate(item)


@router.get("", response_model=list[MarketDataResponse])
def list_market_data(
    product_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> list[MarketDataResponse]:
    items = MarketDataService(db).list(product_id=product_id, limit=limit)
    return [MarketDataResponse.model_validate(i) for i in items]
