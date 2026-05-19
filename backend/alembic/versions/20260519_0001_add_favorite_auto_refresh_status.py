"""Add favorite auto refresh status fields.

Revision ID: 20260519_0001
Revises: 20260424_0002
Create Date: 2026-05-19 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "20260519_0001"
down_revision = "20260424_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.favorite_strategies') IS NOT NULL THEN
                ALTER TABLE favorite_strategies
                    ADD COLUMN IF NOT EXISTS auto_refresh_status VARCHAR NULL,
                    ADD COLUMN IF NOT EXISTS auto_refresh_error TEXT NULL,
                    ADD COLUMN IF NOT EXISTS auto_refresh_started_at TIMESTAMP NULL,
                    ADD COLUMN IF NOT EXISTS auto_refresh_completed_at TIMESTAMP NULL,
                    ADD COLUMN IF NOT EXISTS auto_refresh_run_id VARCHAR NULL;
            END IF;
        END $$;
        """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.favorite_strategies') IS NOT NULL THEN
                ALTER TABLE favorite_strategies
                    DROP COLUMN IF EXISTS auto_refresh_run_id,
                    DROP COLUMN IF EXISTS auto_refresh_completed_at,
                    DROP COLUMN IF EXISTS auto_refresh_started_at,
                    DROP COLUMN IF EXISTS auto_refresh_error,
                    DROP COLUMN IF EXISTS auto_refresh_status;
            END IF;
        END $$;
        """)
