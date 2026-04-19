"""add role column to users

Revision ID: 20260419_0002
Revises: 20260419_0001
Create Date: 2026-04-19 00:00:02
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260419_0002"
down_revision = "20260419_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" not in columns:
        op.add_column("users", sa.Column("role", sa.String(length=30), nullable=False, server_default="analyst"))
        op.execute("UPDATE users SET role = 'analyst' WHERE role IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" in columns:
        op.drop_column("users", "role")
