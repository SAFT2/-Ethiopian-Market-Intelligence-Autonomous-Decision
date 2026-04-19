from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.products_service import ProductsService


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
) -> ProductResponse:
    item = ProductsService(db).create(payload)
    return ProductResponse.model_validate(item)


@router.get("", response_model=list[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> list[ProductResponse]:
    items = ProductsService(db).list(skip=skip, limit=limit)
    return [ProductResponse.model_validate(i) for i in items]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator", "analyst")),
) -> ProductResponse:
    item = ProductsService(db).get(product_id)
    return ProductResponse.model_validate(item)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "operator")),
) -> ProductResponse:
    item = ProductsService(db).update(product_id, payload)
    return ProductResponse.model_validate(item)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    ProductsService(db).delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
