"""Scalp user state horizon / exit columns (#1006).

Revision ID: 20260921_0002
Revises: 20260921_0001
Create Date: 2026-09-21 18:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260921_0002"
down_revision = "20260921_0001"
branch_labels = None
depends_on = None

TABLE = "scalp_user_states"

_NEW_COLUMNS: tuple[tuple[str, str], ...] = (
    ("rest_role", "VARCHAR(8)"),
    ("rest_opened_at", "TIMESTAMP WITHOUT TIME ZONE"),
    ("position_opened_at", "TIMESTAMP WITHOUT TIME ZONE"),
    ("horizon_s", "INTEGER NOT NULL DEFAULT 900"),
    ("last_trade_bp", "NUMERIC(36, 18)"),
    ("last_trade_quote", "NUMERIC(36, 18)"),
    ("stuck", "BOOLEAN NOT NULL DEFAULT FALSE"),
)


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_table(TABLE):
        return
    bind = op.get_bind()
    for name, ddl in _NEW_COLUMNS:
        if _has_column(TABLE, name):
            continue
        bind.execute(sa.text(f"ALTER TABLE {TABLE} ADD COLUMN IF NOT EXISTS {name} {ddl}"))


def downgrade() -> None:
    if not _has_table(TABLE):
        return
    for name, _ddl in reversed(_NEW_COLUMNS):
        if _has_column(TABLE, name):
            op.drop_column(TABLE, name)
