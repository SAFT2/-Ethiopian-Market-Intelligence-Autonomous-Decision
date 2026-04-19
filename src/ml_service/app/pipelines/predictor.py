from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np

from app.models.persistence import ModelStore
from app.schemas.contracts import (
    AnomalyPredictRequest,
    DemandPredictRequest,
    PredictResponse,
    ProductScorePredictRequest,
)


@dataclass(slots=True)
class Predictor:
    store: ModelStore

    def predict_demand(self, req: DemandPredictRequest) -> PredictResponse:
        persisted = self.store.load_latest("demand_forecasting")
        series = np.array(req.history_prices, dtype=float)

        features = np.array(
            [
                [
                    series[-1],
                    series[-1] if len(series) < 7 else series[-7],
                    float(series[-7:].mean()),
                ]
            ]
        )
        pred = float(persisted.model.predict(features)[0])
        return PredictResponse(
            model_name=persisted.model_name,
            model_version=persisted.model_version,
            prediction=pred,
            metadata={"product_id": req.product_id, "location": req.location},
            predicted_at=datetime.now(UTC),
        )

    def predict_product_score(self, req: ProductScorePredictRequest) -> PredictResponse:
        persisted = self.store.load_latest("product_scoring")
        features = np.array(
            [
                [
                    req.avg_monthly_sales,
                    req.avg_margin_pct,
                    req.demand_growth_pct,
                    req.stockout_rate,
                    req.market_volatility,
                ]
            ]
        )

        prob_good = float(persisted.model.predict_proba(features)[0][1])
        return PredictResponse(
            model_name=persisted.model_name,
            model_version=persisted.model_version,
            prediction=prob_good,
            metadata={"classification": "good_investment" if prob_good >= 0.5 else "bad_investment"},
            predicted_at=datetime.now(UTC),
        )

    def predict_anomaly(self, req: AnomalyPredictRequest) -> PredictResponse:
        persisted = self.store.load_latest("anomaly_detection")
        prices = np.array(req.recent_prices, dtype=float)

        delta = 0.0
        if len(prices) > 1 and prices[-2] != 0:
            delta = ((prices[-1] - prices[-2]) / prices[-2]) * 100.0

        features = np.array([[prices[-1], float(len(prices)), delta]])
        label = int(persisted.model.predict(features)[0])
        score = float(persisted.model.decision_function(features)[0])

        return PredictResponse(
            model_name=persisted.model_name,
            model_version=persisted.model_version,
            prediction=float(1 if label == -1 else 0),
            metadata={"is_anomaly": label == -1, "anomaly_score": score},
            predicted_at=datetime.now(UTC),
        )
