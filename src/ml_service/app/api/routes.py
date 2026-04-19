from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.pipelines.predictor import Predictor
from app.pipelines.training import TrainingPipeline
from app.schemas.contracts import (
    AnomalyPredictRequest,
    AnomalyTrainRequest,
    DemandPredictRequest,
    DemandTrainRequest,
    PredictResponse,
    ProductScorePredictRequest,
    ProductScoringTrainRequest,
    TrainResponse,
)


def build_router(training: TrainingPipeline, predictor: Predictor) -> APIRouter:
    router = APIRouter(prefix="/api/v1/ml", tags=["ML Service"])

    @router.post("/train/demand", response_model=TrainResponse)
    def train_demand(payload: DemandTrainRequest) -> TrainResponse:
        try:
            model = training.train_demand_forecasting(payload.csv_path)
            return TrainResponse(
                model_name=model.model_name,
                model_version=model.model_version,
                metrics=model.metadata.get("metrics", {}),
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/train/product-scoring", response_model=TrainResponse)
    def train_product_scoring(payload: ProductScoringTrainRequest) -> TrainResponse:
        try:
            model = training.train_product_scoring(payload.csv_path)
            return TrainResponse(
                model_name=model.model_name,
                model_version=model.model_version,
                metrics=model.metadata.get("metrics", {}),
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/train/anomaly", response_model=TrainResponse)
    def train_anomaly(payload: AnomalyTrainRequest) -> TrainResponse:
        try:
            model = training.train_anomaly_detection(payload.csv_path)
            return TrainResponse(
                model_name=model.model_name,
                model_version=model.model_version,
                metrics=model.metadata.get("metrics", {}),
            )
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/predict/demand", response_model=PredictResponse)
    def predict_demand(payload: DemandPredictRequest) -> PredictResponse:
        try:
            return predictor.predict_demand(payload)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/predict/product-score", response_model=PredictResponse)
    def predict_product_score(payload: ProductScorePredictRequest) -> PredictResponse:
        try:
            return predictor.predict_product_score(payload)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @router.post("/predict/anomaly", response_model=PredictResponse)
    def predict_anomaly(payload: AnomalyPredictRequest) -> PredictResponse:
        try:
            return predictor.predict_anomaly(payload)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return router
