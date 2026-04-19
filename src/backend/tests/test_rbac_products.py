from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[3]
BACKEND_SRC = ROOT / "src" / "backend"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from app.api.deps import get_current_user
from app.core.database import get_db
from app.main import create_app
from app.services.products_service import ProductsService


@dataclass
class FakeUser:
    email: str
    role: str
    is_active: bool = True


def _dummy_db_override():
    yield object()


def test_products_create_forbidden_for_analyst() -> None:
    app = create_app()
    app.dependency_overrides[get_db] = _dummy_db_override
    app.dependency_overrides[get_current_user] = lambda: FakeUser(email="a@test.com", role="analyst")

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/products",
            json={
                "name": "Teff",
                "category": "Grains",
                "brand": "Farm",
                "unit": "kg",
                "description": "test",
            },
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"]["message"] == "Insufficient permissions"


def test_products_create_allowed_for_operator(monkeypatch) -> None:
    app = create_app()
    app.dependency_overrides[get_db] = _dummy_db_override
    app.dependency_overrides[get_current_user] = lambda: FakeUser(email="o@test.com", role="operator")

    class StubProduct:
        id = 101
        name = "Teff"
        category = "Grains"
        brand = "Farm"
        unit = "kg"
        description = "test"
        created_at = datetime.now(UTC)
        updated_at = datetime.now(UTC)

    monkeypatch.setattr(ProductsService, "create", lambda self, payload: StubProduct())

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/products",
            json={
                "name": "Teff",
                "category": "Grains",
                "brand": "Farm",
                "unit": "kg",
                "description": "test",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 101
    assert payload["name"] == "Teff"
