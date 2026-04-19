# FastAPI Backend

Run with:

```bash
uvicorn app.main:app --reload --app-dir src/backend
```

API prefix: `/api/v1`

## Migrations (Alembic)

```bash
cd src/backend
alembic -c alembic.ini upgrade head
```

## Hardening Tests

```bash
pytest src/backend/tests -q
```
