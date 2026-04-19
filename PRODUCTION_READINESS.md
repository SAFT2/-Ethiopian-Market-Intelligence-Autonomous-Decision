# Production Readiness Refinement

## Scalability Improvements

1. Split training jobs from online inference with a queue (Celery/Temporal/Kafka).
2. Replace local model store with object storage + model registry.
3. Add Redis cache for frequent market trend and prediction reads.
4. Add database partitioning for market data time-series tables.

## Redundancy Reduction

1. Centralize shared schemas in a contracts package used by backend and ML service.
2. Move duplicated feature engineering logic into reusable transformer modules.
3. Standardize API error envelope across all services.

## Edge Cases to Handle

1. Sparse history (< 3 points) for demand predictor fallback.
2. Extreme or malformed prices (0, negative, very high outliers).
3. Service partial outage (ML up, DB down; DB up, ML down).
4. Drift in source scraping structure causing missing fields.
5. Highly volatile markets generating frequent anomaly flags.

## Production Controls

1. Add JWT role scopes and route-level authorization.
2. Add rate limiting and request id tracing.
3. Use Alembic migrations (remove startup create_all in backend).
4. Add SLO alerts for backend latency and ML inference failures.
5. Add canary model rollout and shadow evaluation before promotion.
