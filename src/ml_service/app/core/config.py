from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_dir: str
    default_horizon_days: int = 7


def load_settings() -> Settings:
    model_dir = os.getenv("ML_MODEL_DIR", "src/ml_service/model_store")
    return Settings(model_dir=model_dir)
