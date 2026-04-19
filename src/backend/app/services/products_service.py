from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ProductCreate) -> Product:
        now = datetime.now(UTC)
        item = Product(
            name=payload.name,
            category=payload.category,
            brand=payload.brand,
            unit=payload.unit,
            description=payload.description,
            created_at=now,
            updated_at=now,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, skip: int = 0, limit: int = 50) -> list[Product]:
        return self.db.query(Product).offset(skip).limit(limit).all()

    def get(self, product_id: int) -> Product:
        item = self.db.query(Product).filter(Product.id == product_id).first()
        if item is None:
            raise NotFoundError("Product", product_id)
        return item

    def update(self, product_id: int, payload: ProductUpdate) -> Product:
        item = self.get(product_id)
        updates = payload.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(item, key, value)
        item.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, product_id: int) -> None:
        item = self.get(product_id)
        self.db.delete(item)
        self.db.commit()
