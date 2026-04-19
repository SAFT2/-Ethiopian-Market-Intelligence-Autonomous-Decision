from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class MarketListingRecord(Base):
    __tablename__ = "market_listing_record"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    price_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    price_currency: Mapped[str] = mapped_column(String(10), nullable=False, default="ETB")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    listed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    listing_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    unique_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    inserted_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=datetime.utcnow)


def build_engine(database_url: str):
    return create_engine(
        database_url,
        pool_pre_ping=True,
        future=True,
    )


def build_session_factory(database_url: str):
    engine = build_engine(database_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def create_tables(database_url: str) -> None:
    engine = build_engine(database_url)
    Base.metadata.create_all(bind=engine)
