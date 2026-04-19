from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.model_selection import train_test_split

from app.models.persistence import ModelStore, PersistedModel


@dataclass(slots=True)
class TrainingPipeline:
    store: ModelStore

    def train_demand_forecasting(self, csv_path: str) -> PersistedModel:
        df = pd.read_csv(csv_path)
        required = ["lag_1", "lag_7", "rolling_mean_7", "target_next_day"]
        self._validate_columns(df, required)

        x = df[["lag_1", "lag_7", "rolling_mean_7"]].astype(float)
        y = df["target_next_day"].astype(float)

        model = LinearRegression()
        model.fit(x, y)
        preds = model.predict(x)
        mae = float(mean_absolute_error(y, preds))

        return self.store.save(
            model_name="demand_forecasting",
            model=model,
            metrics={"mae": mae},
            extra_metadata={"feature_order": ["lag_1", "lag_7", "rolling_mean_7"]},
        )

    def train_product_scoring(self, csv_path: str) -> PersistedModel:
        df = pd.read_csv(csv_path)
        required = [
            "avg_monthly_sales",
            "avg_margin_pct",
            "demand_growth_pct",
            "stockout_rate",
            "market_volatility",
            "label",
        ]
        self._validate_columns(df, required)

        x = df[
            [
                "avg_monthly_sales",
                "avg_margin_pct",
                "demand_growth_pct",
                "stockout_rate",
                "market_volatility",
            ]
        ].astype(float)
        y = df["label"].astype(int)

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42, stratify=y
        )
        model = RandomForestClassifier(n_estimators=200, random_state=42)
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        acc = float(accuracy_score(y_test, preds))

        return self.store.save(
            model_name="product_scoring",
            model=model,
            metrics={"accuracy": acc},
            extra_metadata={
                "feature_order": [
                    "avg_monthly_sales",
                    "avg_margin_pct",
                    "demand_growth_pct",
                    "stockout_rate",
                    "market_volatility",
                ]
            },
        )

    def train_anomaly_detection(self, csv_path: str) -> PersistedModel:
        df = pd.read_csv(csv_path)
        required = ["price", "volume", "daily_delta_pct"]
        self._validate_columns(df, required)

        x = df[["price", "volume", "daily_delta_pct"]].astype(float)
        model = IsolationForest(contamination=0.08, random_state=42)
        model.fit(x)

        raw_preds = model.predict(x)
        outlier_rate = float(np.mean(raw_preds == -1))

        return self.store.save(
            model_name="anomaly_detection",
            model=model,
            metrics={"outlier_rate_train": outlier_rate},
            extra_metadata={"feature_order": ["price", "volume", "daily_delta_pct"]},
        )

    @staticmethod
    def _validate_columns(df: pd.DataFrame, required: list[str]) -> None:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
