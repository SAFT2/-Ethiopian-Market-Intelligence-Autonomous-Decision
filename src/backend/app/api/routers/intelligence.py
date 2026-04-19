from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.deps import require_roles
from app.models.user import User
from app.schemas.intelligence import IntelligenceRequest, IntelligenceResponse
from app.services.intelligence_service import IntelligenceService


router = APIRouter(prefix="/intelligence", tags=["Intelligence"])
service = IntelligenceService()


@router.post("/evaluate", response_model=IntelligenceResponse)
async def evaluate(
    request: Request,
    payload: IntelligenceRequest,
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> IntelligenceResponse:
    request_id = getattr(request.state, "request_id", None)
    return await service.evaluate(payload, request_id=request_id)
