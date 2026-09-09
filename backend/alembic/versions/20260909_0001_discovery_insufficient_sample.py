"""Add discovery sweep insufficient_sample counter and widen eligibility.

Revision ID: 20260909_0001
Revises: 20260823_0001
Create Date: 2026-09-09 12:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260909_0001"
down_revision = "20260823_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "discovery_sweeps",
        sa.Column(
            "insufficient_sample",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    # "insufficient_sample" is 19 chars; the original VARCHAR(16) cannot store it.
    op.alter_column(
        "discovery_results",
        "eligibility",
        existing_type=sa.String(length=16),
        type_=sa.String(length=32),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "discovery_results",
        "eligibility",
        existing_type=sa.String(length=32),
        type_=sa.String(length=16),
        existing_nullable=False,
    )
    op.drop_column("discovery_sweeps", "insufficient_sample")
