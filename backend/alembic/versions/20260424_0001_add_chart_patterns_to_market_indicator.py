"""Add chart pattern events to market indicators.

Revision ID: 20260424_0001
Revises: 20260423_0001
Create Date: 2026-04-24 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "20260424_0001"
down_revision = "20260423_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.market_indicator') IS NOT NULL THEN
                ALTER TABLE market_indicator ADD COLUMN IF NOT EXISTS chart_patterns JSONB;
            END IF;
        END $$;
        """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.market_indicator') IS NOT NULL THEN
                ALTER TABLE market_indicator DROP COLUMN IF EXISTS chart_patterns;
            END IF;
        END $$;
        """)
