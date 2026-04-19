from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[3]
BACKEND_SRC = ROOT / "src" / "backend"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from app.services.intelligence_service import IntelligenceService


class _FakeResponse:
    def __init__(self, payload: dict | None = None, fail: bool = False) -> None:
        self._payload = payload or {}
        self._fail = fail

    def raise_for_status(self) -> None:
        if self._fail:
            raise httpx.HTTPStatusError("bad", request=None, response=None)

    def json(self) -> dict:
        return self._payload


@pytest.mark.asyncio
async def test_ml_retries_then_success(monkeypatch) -> None:
    service = IntelligenceService()
    service.max_retries = 3
    service.failure_threshold = 99

    state = {"count": 0}

    class _FakeClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers=None):
            state["count"] += 1
            if state["count"] < 3:
                raise httpx.ConnectError("temporary", request=None)
            return _FakeResponse(payload={"prediction": 42.0})

    monkeypatch.setattr("app.services.intelligence_service.httpx.AsyncClient", _FakeClient)

    result = await service._post_ml("/api/v1/ml/predict/demand", {"x": 1})
    assert result["prediction"] == 42.0
    assert state["count"] == 3


@pytest.mark.asyncio
async def test_ml_circuit_breaker_opens(monkeypatch) -> None:
    service = IntelligenceService()
    service.max_retries = 1
    service.failure_threshold = 2
    service.circuit_open_seconds = 120

    state = {"count": 0}

    class _FailClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url: str, json: dict, headers=None):
            state["count"] += 1
            raise httpx.ConnectError("down", request=None)

    monkeypatch.setattr("app.services.intelligence_service.httpx.AsyncClient", _FailClient)

    with pytest.raises(HTTPException) as first:
        await service._post_ml("/api/v1/ml/predict/demand", {"x": 1})
    assert first.value.status_code == 502

    with pytest.raises(HTTPException) as second:
        await service._post_ml("/api/v1/ml/predict/demand", {"x": 1})
    assert second.value.status_code == 502

    with pytest.raises(HTTPException) as third:
        await service._post_ml("/api/v1/ml/predict/demand", {"x": 1})
    assert third.value.status_code == 503
    assert "circuit breaker is open" in str(third.value.detail)

    assert state["count"] == 2
