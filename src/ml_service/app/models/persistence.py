from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib


@dataclass(slots=True)
class PersistedModel:
    model_name: str
    model_version: str
    model: Any
    metadata: dict


class ModelStore:
    """Filesystem model store using joblib + json metadata."""

    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def save(self, model_name: str, model: Any, metrics: dict, extra_metadata: dict | None = None) -> PersistedModel:
        version = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        target_dir = self.base / model_name / version
        target_dir.mkdir(parents=True, exist_ok=True)

        model_path = target_dir / "model.joblib"
        meta_path = target_dir / "metadata.json"

        metadata = {
            "model_name": model_name,
            "model_version": version,
            "trained_at": datetime.now(UTC).isoformat(),
            "metrics": metrics,
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        joblib.dump(model, model_path)
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return PersistedModel(model_name=model_name, model_version=version, model=model, metadata=metadata)

    def load_latest(self, model_name: str) -> PersistedModel:
        model_dir = self.base / model_name
        if not model_dir.exists():
            raise FileNotFoundError(f"No model found for {model_name}")

        versions = sorted([d for d in model_dir.iterdir() if d.is_dir()])
        if not versions:
            raise FileNotFoundError(f"No versions found for {model_name}")

        latest = versions[-1]
        model = joblib.load(latest / "model.joblib")
        metadata = json.loads((latest / "metadata.json").read_text(encoding="utf-8"))

        return PersistedModel(
            model_name=model_name,
            model_version=metadata.get("model_version", latest.name),
            model=model,
            metadata=metadata,
        )
