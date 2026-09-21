"""Per-user directional scalp switch and fills (#1001).

Revision ID: 20260921_0001
Revises: 20260915_0001
Create Date: 2026-09-21 12:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260921_0001"
down_revision = "20260915_0001"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _has_table("scalp_user_states"):
        op.create_table(
            "scalp_user_states",
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("killed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("inventory_btc", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("floor_btc", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("avg_entry_quote", sa.Numeric(36, 18), nullable=True),
            sa.Column("realized_pnl_quote", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("fees_quote", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("jev_cost_quote", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("day_pnl_quote", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("day_started_at", sa.DateTime(), nullable=True),
            sa.Column("calibration_hits", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("calibration_signals", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("last_jev_latency_ms", sa.Integer(), nullable=True),
            sa.Column("last_jev_at", sa.DateTime(), nullable=True),
            sa.Column("jev_in_flight", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("rest_client_order_id", sa.String(length=36), nullable=True),
            sa.Column("rest_side", sa.String(length=8), nullable=True),
            sa.Column("rest_price", sa.Numeric(36, 18), nullable=True),
            sa.Column("inventory_clipped", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("user_id"),
        )
    if not _has_table("scalp_fills"):
        op.create_table(
            "scalp_fills",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("client_order_id", sa.String(length=36), nullable=False),
            sa.Column("side", sa.String(length=8), nullable=False),
            sa.Column("quantity", sa.Numeric(36, 18), nullable=False),
            sa.Column("price", sa.Numeric(36, 18), nullable=False),
            sa.Column("fee_quote", sa.Numeric(36, 18), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "client_order_id", "side", "quantity", "price", name="uq_scalp_fills_leg"
            ),
        )
        op.create_index("ix_scalp_fills_user_id", "scalp_fills", ["user_id"])
        op.create_index("ix_scalp_fills_user_created", "scalp_fills", ["user_id", "created_at"])


def downgrade() -> None:
    if _has_table("scalp_fills"):
        op.drop_index("ix_scalp_fills_user_created", table_name="scalp_fills")
        op.drop_index("ix_scalp_fills_user_id", table_name="scalp_fills")
        op.drop_table("scalp_fills")
    if _has_table("scalp_user_states"):
        op.drop_table("scalp_user_states")
