"""Jev closed-day diagnosis, applied versions and paused calibration (#1045).

Revision ID: 20260927_0001
Revises: 20260921_0002
Create Date: 2026-09-27 00:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260927_0001"
down_revision = "20260921_0002"
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _has_table("scalp_jev_diagnoses"):
        op.create_table(
            "scalp_jev_diagnoses",
            sa.Column("closed_day", sa.Date(), nullable=False),
            sa.Column("run_at", sa.DateTime(), nullable=False),
            sa.Column("period_start", sa.DateTime(), nullable=True),
            sa.Column("period_end", sa.DateTime(), nullable=True),
            sa.Column("measurement_status", sa.String(length=32), nullable=False),
            sa.Column("verb", sa.String(length=16), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("operator_reason", sa.Text(), nullable=False),
            sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("block_kind", sa.String(length=32), nullable=True),
            sa.Column("posterior_n", sa.Integer(), nullable=True),
            sa.Column("operable", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("fingerprint", sa.String(length=64), nullable=True),
            sa.Column("applied_version_id", sa.String(length=36), nullable=True),
            sa.Column("panel_json", sa.Text(), nullable=True),
            sa.Column("summary_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("closed_day"),
        )
    if not _has_table("scalp_confidence_versions"):
        op.create_table(
            "scalp_confidence_versions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("version_n", sa.Integer(), nullable=False),
            sa.Column("fingerprint", sa.String(length=64), nullable=False),
            sa.Column("policies_json", sa.Text(), nullable=False),
            sa.Column("previous_id", sa.String(length=36), nullable=True),
            sa.Column("applied_at", sa.DateTime(), nullable=False),
            sa.Column("applied_for_day", sa.Date(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("source", sa.String(length=24), nullable=False),
            sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("choice_until", sa.DateTime(), nullable=True),
            sa.Column("validated_until", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("version_n", name="uq_scalp_confidence_versions_n"),
            sa.UniqueConstraint("fingerprint", name="uq_scalp_confidence_versions_fp"),
        )
    if not _has_table("scalp_calibration_state"):
        op.create_table(
            "scalp_calibration_state",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("paused", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("suppressed_fingerprint", sa.String(length=64), nullable=True),
            sa.Column("suppressed_day", sa.Date(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.execute(
            sa.text(
                "INSERT INTO scalp_calibration_state (id, paused, updated_at) "
                "VALUES (1, TRUE, CURRENT_TIMESTAMP)"
            )
        )


def downgrade() -> None:
    if _has_table("scalp_calibration_state"):
        op.drop_table("scalp_calibration_state")
    if _has_table("scalp_confidence_versions"):
        op.drop_table("scalp_confidence_versions")
    if _has_table("scalp_jev_diagnoses"):
        op.drop_table("scalp_jev_diagnoses")
