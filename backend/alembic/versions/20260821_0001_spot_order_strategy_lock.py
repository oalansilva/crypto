"""Lock unresolved Spot orders by strategy symbol (USDT pair).

Revision ID: 20260821_0001
Revises: 20260818_0001
Create Date: 2026-08-21 13:15:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260821_0001"
down_revision = "20260818_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "monitor_spot_order_requests",
        sa.Column("strategy_symbol", sa.String(length=32), nullable=True),
    )
    op.execute(
        """
        UPDATE monitor_spot_order_requests
        SET strategy_symbol = symbol
        WHERE strategy_symbol IS NULL
        """
    )
    op.alter_column(
        "monitor_spot_order_requests",
        "strategy_symbol",
        existing_type=sa.String(length=32),
        nullable=False,
    )
    op.create_index(
        "ix_monitor_spot_order_requests_strategy_symbol",
        "monitor_spot_order_requests",
        ["strategy_symbol"],
        unique=False,
    )
    op.drop_index(
        "uq_monitor_spot_order_requests_unresolved_symbol",
        table_name="monitor_spot_order_requests",
    )
    op.create_index(
        "uq_monitor_spot_order_requests_unresolved_strategy",
        "monitor_spot_order_requests",
        ["user_id", "strategy_symbol"],
        unique=True,
        postgresql_where=sa.text("state IN ('submitting', 'reconciling')"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_monitor_spot_order_requests_unresolved_strategy",
        table_name="monitor_spot_order_requests",
    )
    op.create_index(
        "uq_monitor_spot_order_requests_unresolved_symbol",
        "monitor_spot_order_requests",
        ["user_id", "symbol"],
        unique=True,
        postgresql_where=sa.text("state IN ('submitting', 'reconciling')"),
    )
    op.drop_index(
        "ix_monitor_spot_order_requests_strategy_symbol",
        table_name="monitor_spot_order_requests",
    )
    op.drop_column("monitor_spot_order_requests", "strategy_symbol")
