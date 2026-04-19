"""initial backend schema

Revision ID: 20260419_0001
Revises: 
Create Date: 2026-04-19 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260419_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False, server_default="analyst"),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=True),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_category"), "products", ["category"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)

    op.create_table(
        "market_data_points",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("price_value", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("listing_url", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_market_data_points_created_at"), "market_data_points", ["created_at"], unique=False)
    op.create_index(op.f("ix_market_data_points_location"), "market_data_points", ["location"], unique=False)
    op.create_index(op.f("ix_market_data_points_observed_at"), "market_data_points", ["observed_at"], unique=False)
    op.create_index(op.f("ix_market_data_points_price_value"), "market_data_points", ["price_value"], unique=False)
    op.create_index(op.f("ix_market_data_points_product_id"), "market_data_points", ["product_id"], unique=False)
    op.create_index(op.f("ix_market_data_points_product_name"), "market_data_points", ["product_name"], unique=False)
    op.create_index(op.f("ix_market_data_points_source"), "market_data_points", ["source"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False),
        sa.Column("predicted_price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("predicted_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_model_name"), "predictions", ["model_name"], unique=False)
    op.create_index(op.f("ix_predictions_predicted_for"), "predictions", ["predicted_for"], unique=False)
    op.create_index(op.f("ix_predictions_product_id"), "predictions", ["product_id"], unique=False)

    op.create_table(
        "decisions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=True),
        sa.Column("decision_type", sa.String(length=60), nullable=False),
        sa.Column("recommendation", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("risk_score", sa.Numeric(precision=6, scale=3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decisions_decision_type"), "decisions", ["decision_type"], unique=False)
    op.create_index(op.f("ix_decisions_product_id"), "decisions", ["product_id"], unique=False)
    op.create_index(op.f("ix_decisions_status"), "decisions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_decisions_status"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_product_id"), table_name="decisions")
    op.drop_index(op.f("ix_decisions_decision_type"), table_name="decisions")
    op.drop_table("decisions")

    op.drop_index(op.f("ix_predictions_product_id"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_predicted_for"), table_name="predictions")
    op.drop_index(op.f("ix_predictions_model_name"), table_name="predictions")
    op.drop_table("predictions")

    op.drop_index(op.f("ix_market_data_points_source"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_product_name"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_product_id"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_price_value"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_observed_at"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_location"), table_name="market_data_points")
    op.drop_index(op.f("ix_market_data_points_created_at"), table_name="market_data_points")
    op.drop_table("market_data_points")

    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_category"), table_name="products")
    op.drop_table("products")

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
