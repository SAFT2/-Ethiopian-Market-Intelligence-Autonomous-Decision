# Integration Guide

## Service Topology

- Frontend (`src/frontend`) calls Backend API (`src/backend`) via Axios.
- Backend endpoint `/api/v1/intelligence/evaluate` calls ML Service (`src/ml_service`) via HTTP.
- Backend applies Decision Engine (`src/decision_engine`) to ML outputs + internal inputs.

## Run Order

1. Start ML service on port 8010:
   - `uvicorn app.main:app --reload --port 8010 --app-dir src/ml_service`
2. Start backend on port 8000:
   - `ML_SERVICE_BASE_URL=http://localhost:8010 uvicorn app.main:app --reload --port 8000 --app-dir src/backend`
3. Start frontend on port 5173:
   - `cd src/frontend && npm install && npm run dev`

## Data Flow

1. Scraper pipeline writes cleaned market data into PostgreSQL.
2. Frontend requests market data from backend `GET /api/v1/market-data`.
3. Frontend triggers intelligence evaluation with `POST /api/v1/intelligence/evaluate`.
4. Backend calls ML prediction endpoints:
   - `/api/v1/ml/predict/demand`
   - `/api/v1/ml/predict/product-score`
   - `/api/v1/ml/predict/anomaly`
5. Backend combines outputs through decision engine and returns explainable decision payload.

## Key Integration Snippet

```python
# src/backend/app/services/intelligence_service.py
response = await client.post(f"{self.ml_base_url}/api/v1/ml/predict/demand", json=payload)
result = self.engine.evaluate(DecisionInput(...))
```

## Testing Strategy

1. Unit tests:
   - ML feature/shape validation in training and predictor pipelines.
   - Decision engine rule and scoring outcomes.
2. Contract tests:
   - Backend -> ML endpoint payload/response schema compatibility.
3. Integration tests:
   - Happy path: market data -> intelligence evaluation -> decision explanation.
   - Failure path: ML service unavailable returns 502 from backend.
4. Frontend E2E:
   - Dashboard loads trends.
   - Generate decision button updates AI panel.
   - What-if simulation reacts to slider changes.
