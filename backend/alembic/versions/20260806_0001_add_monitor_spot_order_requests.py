"""Add durable Monitor direct Spot order request records.

Revision ID: 20260806_0001
Revises: 20260803_0001
Create Date: 2026-08-06 18:55:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260806_0001"
down_revision = "20260803_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "monitor_spot_order_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("client_order_id", sa.String(length=36), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("submitting_account_identity_hash", sa.String(length=64), nullable=False),
        sa.Column("requested_quote_amount", sa.Numeric(36, 18), nullable=True),
        sa.Column("calculated_base_quantity", sa.Numeric(36, 18), nullable=True),
        sa.Column("executed_base_quantity", sa.Numeric(36, 18), nullable=True),
        sa.Column("executed_quote_amount", sa.Numeric(36, 18), nullable=True),
        sa.Column("average_price", sa.Numeric(36, 18), nullable=True),
        sa.Column("external_order_id", sa.String(length=64), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_reconciled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "client_order_id", name="uq_monitor_spot_order_requests_client_order_id"
        ),
        sa.UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_monitor_spot_order_requests_user_key",
        ),
    )
    op.create_index(
        "ix_monitor_spot_order_requests_user_id",
        "monitor_spot_order_requests",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_monitor_spot_order_requests_symbol",
        "monitor_spot_order_requests",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        "ix_monitor_spot_order_requests_state",
        "monitor_spot_order_requests",
        ["state"],
        unique=False,
    )
    op.create_index(
        "ix_monitor_spot_order_requests_user_state_created",
        "monitor_spot_order_requests",
        ["user_id", "state", "created_at"],
        unique=False,
    )
    op.create_index(
        "uq_monitor_spot_order_requests_unresolved_symbol",
        "monitor_spot_order_requests",
        ["user_id", "symbol"],
        unique=True,
        postgresql_where=sa.text("state IN ('submitting', 'reconciling')"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_monitor_spot_order_requests_unresolved_symbol",
        table_name="monitor_spot_order_requests",
    )
    op.drop_index(
        "ix_monitor_spot_order_requests_user_state_created",
        table_name="monitor_spot_order_requests",
    )
    op.drop_index("ix_monitor_spot_order_requests_state", table_name="monitor_spot_order_requests")
    op.drop_index("ix_monitor_spot_order_requests_symbol", table_name="monitor_spot_order_requests")
    op.drop_index(
        "ix_monitor_spot_order_requests_user_id", table_name="monitor_spot_order_requests"
    )
    op.drop_table("monitor_spot_order_requests")
