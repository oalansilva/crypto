"""Add pivot support and resistance levels to market indicators.

Revision ID: 20260424_0002
Revises: 20260424_0001
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "20260424_0002"
down_revision = "20260424_0001"
branch_labels = None
depends_on = None


PIVOT_COLUMNS = (
    "pivot_point",
    "support_1",
    "support_2",
    "support_3",
    "resistance_1",
    "resistance_2",
    "resistance_3",
)


def upgrade() -> None:
    for column in PIVOT_COLUMNS:
        op.execute(f"""
            DO $$
            BEGIN
                IF to_regclass('public.market_indicator') IS NOT NULL THEN
                    ALTER TABLE market_indicator ADD COLUMN IF NOT EXISTS {column} NUMERIC;
                END IF;
            END $$;
            """)


def downgrade() -> None:
    for column in reversed(PIVOT_COLUMNS):
        op.execute(f"""
            DO $$
            BEGIN
                IF to_regclass('public.market_indicator') IS NOT NULL THEN
                    ALTER TABLE market_indicator DROP COLUMN IF EXISTS {column};
                END IF;
            END $$;
            """)
