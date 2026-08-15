"""Create discovery sweep tables for systematic swing strategy discovery.

Revision ID: 20260814_0001_discovery_sweeps
Revises: 20260806_0001
Create Date: 2026-08-14 22:10:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260814_0001_discovery_sweeps"
down_revision = "20260806_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discovery_sweeps",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("snapshot_token", sa.String(length=64), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("succeeded", sa.Integer(), nullable=False),
        sa.Column("failed", sa.Integer(), nullable=False),
        sa.Column("skipped", sa.Integer(), nullable=False),
        sa.Column("processed", sa.Integer(), nullable=False),
        sa.Column("terminal_reason", sa.String(length=64), nullable=True),
        sa.Column("terminal_code", sa.String(length=64), nullable=True),
        sa.Column("cancellation_requested", sa.Boolean(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("actor", "idempotency_key", name="uq_discovery_sweeps_actor_key"),
    )
    op.create_index("ix_discovery_sweeps_state", "discovery_sweeps", ["state"], unique=False)
    op.create_index("ix_discovery_sweeps_actor", "discovery_sweeps", ["actor"], unique=False)

    op.create_table(
        "discovery_combinations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("sweep_id", sa.String(length=64), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("direction", sa.String(length=8), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("lease_owner", sa.String(length=128), nullable=True),
        sa.Column("lease_expires_at", sa.DateTime(), nullable=True),
        sa.Column("result_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sweep_id",
            "template_id",
            "symbol",
            "timeframe",
            "direction",
            name="uq_discovery_combinations_key",
        ),
    )
    op.create_index(
        "ix_discovery_combinations_sweep_state",
        "discovery_combinations",
        ["sweep_id", "state"],
        unique=False,
    )
    op.create_index(
        "ix_discovery_combinations_lease",
        "discovery_combinations",
        ["lease_owner", "lease_expires_at"],
        unique=False,
    )

    op.create_table(
        "discovery_results",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("sweep_id", sa.String(length=64), nullable=False),
        sa.Column("combination_id", sa.BigInteger(), nullable=False),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("template_version", sa.String(length=32), nullable=True),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("direction", sa.String(length=8), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("candle_source", sa.String(length=32), nullable=True),
        sa.Column("candle_version", sa.String(length=32), nullable=True),
        sa.Column("expected_candles", sa.Integer(), nullable=True),
        sa.Column("observed_valid_candles", sa.Integer(), nullable=True),
        sa.Column("coverage", sa.Float(), nullable=True),
        sa.Column("fees_slippage", sa.JSON(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("trades_count", sa.Integer(), nullable=True),
        sa.Column("win_rate", sa.Float(), nullable=True),
        sa.Column("sharpe_ratio", sa.Float(), nullable=True),
        sa.Column("profit_factor", sa.Float(), nullable=True),
        sa.Column("max_drawdown", sa.Float(), nullable=True),
        sa.Column("calmar_ratio", sa.Float(), nullable=True),
        sa.Column("cagr", sa.Float(), nullable=True),
        sa.Column("benchmark_cagr", sa.Float(), nullable=True),
        sa.Column("delta_cagr_vs_bh", sa.Float(), nullable=True),
        sa.Column("strategy_identity_key", sa.String(length=64), nullable=False),
        sa.Column("evidence_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("eligibility", sa.String(length=16), nullable=False),
        sa.Column("eligibility_reason", sa.String(length=128), nullable=True),
        sa.Column("dedup_state", sa.String(length=32), nullable=False),
        sa.Column("dedup_reference", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("combination_id", name="uq_discovery_results_combination"),
        sa.UniqueConstraint(
            "strategy_identity_key", "sweep_id", name="uq_discovery_results_identity_sweep"
        ),
    )
    op.create_index("ix_discovery_results_sweep", "discovery_results", ["sweep_id"], unique=False)
    op.create_index(
        "ix_discovery_results_identity",
        "discovery_results",
        ["strategy_identity_key"],
        unique=False,
    )
    op.create_index(
        "ix_discovery_results_rank",
        "discovery_results",
        ["sweep_id", "calmar_ratio", "trades_count"],
        unique=False,
    )

    op.create_table(
        "discovery_dedup_evidence",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("result_id", sa.String(length=64), nullable=False),
        sa.Column("classification", sa.String(length=32), nullable=False),
        sa.Column("matched_reference", sa.String(length=64), nullable=True),
        sa.Column("structure_version", sa.String(length=32), nullable=True),
        sa.Column("quantum_version", sa.String(length=32), nullable=True),
        sa.Column("compared_dimensions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_discovery_dedup_evidence_result",
        "discovery_dedup_evidence",
        ["result_id"],
        unique=False,
    )

    op.create_table(
        "discovery_outbox",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("sweep_id", sa.String(length=64), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("acked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_discovery_outbox_state", "discovery_outbox", ["state", "created_at"], unique=False
    )
    op.create_index("ix_discovery_outbox_sweep", "discovery_outbox", ["sweep_id"], unique=False)

    op.create_table(
        "discovery_idempotency",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=32), nullable=False),
        sa.Column("resource_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("actor", "idempotency_key", name="uq_discovery_idempotency_actor_key"),
    )
    op.create_index(
        "ix_discovery_idempotency_actor", "discovery_idempotency", ["actor"], unique=False
    )


def downgrade() -> None:
    op.drop_table("discovery_idempotency")
    op.drop_table("discovery_outbox")
    op.drop_table("discovery_dedup_evidence")
    op.drop_table("discovery_results")
    op.drop_table("discovery_combinations")
    op.drop_table("discovery_sweeps")
