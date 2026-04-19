from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from fastapi import HTTPException, status

try:
    from decision_engine.engine import DecisionEngine, DecisionInput
except ModuleNotFoundError:
    repo_src = Path(__file__).resolve().parents[3]
    if str(repo_src) not in sys.path:
        sys.path.append(str(repo_src))
    from decision_engine.engine import DecisionEngine, DecisionInput

from app.schemas.intelligence import IntelligenceRequest, IntelligenceResponse
from app.core.config import settings


LOGGER = logging.getLogger(__name__)


class IntelligenceService:
    def __init__(self) -> None:
        self.ml_base_url = os.getenv("ML_SERVICE_BASE_URL", settings.ml_service_base_url)
        self.ml_timeout = float(settings.ml_request_timeout_seconds)
        self.max_retries = int(settings.ml_request_max_retries)
        self.failure_threshold = int(settings.ml_circuit_failure_threshold)
        self.circuit_open_seconds = int(settings.ml_circuit_open_seconds)
        self._failure_count = 0
        self._circuit_open_until = 0.0
        self.engine = DecisionEngine()

    async def evaluate(self, req: IntelligenceRequest, request_id: str | None = None) -> IntelligenceResponse:
        demand = await self._predict_demand(req, request_id=request_id)
        product_score = await self._predict_product_score(req, request_id=request_id)
        anomaly_prob = await self._predict_anomaly(req, request_id=request_id)

        decision = self.engine.evaluate(
            DecisionInput(
                current_price=req.current_price,
                avg_market_price=req.avg_market_price,
                inventory_days_cover=req.inventory_days_cover,
                weekly_sales_units=req.weekly_sales_units,
                forecast_demand_units=demand,
                product_score=product_score,
                anomaly_flag=anomaly_prob >= 0.5,
            )
        )

        return IntelligenceResponse(
            product_id=req.product_id,
            demand_forecast=demand,
            product_score=product_score,
            anomaly_probability=anomaly_prob,
            pricing_recommendation=decision.pricing_recommendation,
            stock_decision=decision.stock_decision,
            risk_alert=decision.risk_alert,
            score=decision.score,
            explanation=decision.explanation,
        )

    async def _predict_demand(self, req: IntelligenceRequest, request_id: str | None = None) -> float:
        payload = {
            "product_id": req.product_id,
            "location": req.location,
            "history_prices": req.history_prices,
        }
        response = await self._post_ml("/api/v1/ml/predict/demand", payload, request_id=request_id)
        return float(response["prediction"])

    async def _predict_product_score(self, req: IntelligenceRequest, request_id: str | None = None) -> float:
        margin_proxy = max(0.0, min(1.0, (req.avg_market_price - req.current_price) / req.avg_market_price))
        demand_growth_proxy = 0.0
        if len(req.history_prices) > 1 and req.history_prices[0] > 0:
            demand_growth_proxy = (req.history_prices[-1] - req.history_prices[0]) / req.history_prices[0]

        payload = {
            "avg_monthly_sales": req.weekly_sales_units * 4,
            "avg_margin_pct": margin_proxy,
            "demand_growth_pct": max(-1.0, min(3.0, demand_growth_proxy)),
            "stockout_rate": 1.0 if req.inventory_days_cover < 7 else 0.3 if req.inventory_days_cover < 20 else 0.05,
            "market_volatility": float(abs(req.avg_market_price - req.current_price)),
        }
        response = await self._post_ml("/api/v1/ml/predict/product-score", payload, request_id=request_id)
        return float(response["prediction"])

    async def _predict_anomaly(self, req: IntelligenceRequest, request_id: str | None = None) -> float:
        payload = {"recent_prices": req.history_prices}
        response = await self._post_ml("/api/v1/ml/predict/anomaly", payload, request_id=request_id)
        return float(response["prediction"])

    async def _post_ml(
        self,
        path: str,
        payload: dict[str, Any],
        request_id: str | None = None,
    ) -> dict[str, Any]:
        now = time.time()
        if now < self._circuit_open_until:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"ML circuit breaker is open for {path}",
            )

        url = f"{self.ml_base_url}{path}"
        last_error: Exception | None = None
        headers = {"X-Request-ID": request_id} if request_id else None

        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.ml_timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    if "prediction" not in data:
                        raise ValueError(f"Invalid ML response shape for {path}")
                    self._failure_count = 0
                    return data
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                LOGGER.warning(
                    "ml_request_failure",
                    extra={"request_id": request_id, "path": path, "attempt": attempt},
                )
                if attempt == self.max_retries:
                    break
                await asyncio.sleep(min(0.5 * attempt, 2.0))

        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self._circuit_open_until = time.time() + self.circuit_open_seconds
            LOGGER.error(
                "ml_circuit_opened",
                extra={"request_id": request_id, "path": path},
            )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ML service request failed for {path}: {last_error}",
        )
