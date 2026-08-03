"""Persist the execution direction of the legacy short pullback template.

Revision ID: 20260803_0001
Revises: 20260602_0001
Create Date: 2026-08-03 20:30:00
"""

from __future__ import annotations

from alembic import op

revision = "20260803_0001"
down_revision = "20260602_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE combo_templates
        SET template_data = jsonb_set(
            template_data::jsonb,
            '{direction}',
            '"short"'::jsonb,
            true
        )::text,
            updated_at = CURRENT_TIMESTAMP
        WHERE name = 'short_ema200_pullback';
        """)


def downgrade() -> None:
    op.execute("""
        UPDATE combo_templates
        SET template_data = (template_data::jsonb - 'direction')::text,
            updated_at = CURRENT_TIMESTAMP
        WHERE name = 'short_ema200_pullback';
        """)
