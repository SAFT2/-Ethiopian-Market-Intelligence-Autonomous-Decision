from __future__ import annotations

from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.decisions import router as decisions_router
from app.api.routers.intelligence import router as intelligence_router
from app.api.routers.market_data import router as market_data_router
from app.api.routers.predictions import router as predictions_router
from app.api.routers.products import router as products_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(market_data_router)
api_router.include_router(predictions_router)
api_router.include_router(decisions_router)
api_router.include_router(intelligence_router)
