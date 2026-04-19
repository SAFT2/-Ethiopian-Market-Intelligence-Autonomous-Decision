# Free-Tier Deployment Plan

This project is deployable on free tiers by splitting responsibilities:

1. Frontend: Cloudflare Pages or Render Static Site
2. Backend API: Render free web service
3. ML Service: Render free web service
4. Database: Neon Postgres free tier

## Why this setup

- Keeps managed PostgreSQL without hosting your own DB.
- Supports FastAPI services with minimal ops.
- Preserves architecture separation while staying near-zero cost.

## Option A: Render + Neon (recommended)

1. Create a Neon Postgres project and copy the connection URL.
2. In Render, create services using [deploy/render/render.yaml](deploy/render/render.yaml).
3. Set secrets in Render:
   - DATABASE_URL = Neon connection string
   - JWT_SECRET_KEY = strong random secret
   - CORS_ALLOW_ORIGINS = frontend domain(s), comma-separated
4. Deploy backend and ML service.
5. Deploy frontend static service.

Notes:
- Free web services may sleep after inactivity, causing cold-start latency.
- Keep ML model artifacts small for faster cold start.

## Option B: Frontend on Cloudflare Pages

1. Connect repository to Cloudflare Pages.
2. Build command: `npm ci && npm run build`
3. Output directory: `dist`
4. Set env variable `VITE_BACKEND_URL` to backend API URL.

## Database migration on deploy

Run migration command after backend deploy:

```bash
cd src/backend
alembic -c alembic.ini upgrade head
```

## Cost-control tips

1. Keep ML and backend as two small instances only.
2. Restrict logs and retention to defaults.
3. Avoid always-on workers in free plans.
4. Use caching for frequent reads to reduce DB load.

## Production hardening checklist for free tier

1. Enable strict CORS and JWT secret management.
2. Keep CREATE_TABLES_ON_STARTUP=false.
3. Use CI in [./.github/workflows/ci.yml](.github/workflows/ci.yml) for gatekeeping.
4. Run containerized tests locally with:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```
