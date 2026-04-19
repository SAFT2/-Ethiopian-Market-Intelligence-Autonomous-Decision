from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI
from fastapi import Request

from app.api.routes import build_router
from app.core.config import load_settings
from app.core.logging_utils import configure_logging
from app.models.persistence import ModelStore
from app.pipelines.predictor import Predictor
from app.pipelines.training import TrainingPipeline


configure_logging()
LOGGER = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = load_settings()
    store = ModelStore(settings.model_dir)
    training = TrainingPipeline(store=store)
    predictor = Predictor(store=store)

    app = FastAPI(title="ML Service")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        LOGGER.info("ml_request_start", extra={"request_id": request_id, "path": str(request.url.path)})
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        LOGGER.info(
            "ml_request_end",
            extra={"request_id": request_id, "status_code": response.status_code, "path": str(request.url.path)},
        )
        return response

    app.include_router(build_router(training=training, predictor=predictor))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
