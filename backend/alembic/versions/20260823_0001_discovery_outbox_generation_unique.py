"""Uniqueness of discovery outbox (sweep_id, generation).

Revision ID: 20260823_0001
Revises: 20260821_0001
Create Date: 2026-08-23 00:50:00
"""

from __future__ import annotations

from alembic import op

revision = "20260823_0001"
down_revision = "20260821_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM discovery_outbox AS d
        WHERE d.id NOT IN (
            SELECT MAX(id)
            FROM discovery_outbox
            GROUP BY sweep_id, generation
        )
        """)
    op.create_unique_constraint(
        "uq_discovery_outbox_sweep_generation",
        "discovery_outbox",
        ["sweep_id", "generation"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_discovery_outbox_sweep_generation",
        "discovery_outbox",
        type_="unique",
    )
