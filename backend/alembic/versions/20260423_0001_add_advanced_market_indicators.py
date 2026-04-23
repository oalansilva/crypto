"""Add advanced market indicator columns.

Revision ID: 20260423_0001
Revises: 20260419_0001
Create Date: 2026-04-23 00:00:00
"""

from __future__ import annotations

from alembic import op

revision = "20260423_0001"
down_revision = "20260419_0001"
branch_labels = None
depends_on = None


ADVANCED_COLUMNS = (
    "bb_upper_20_2",
    "bb_middle_20_2",
    "bb_lower_20_2",
    "atr_14",
    "stoch_k_14_3_3",
    "stoch_d_14_3_3",
    "obv",
    "ichimoku_tenkan_9",
    "ichimoku_kijun_26",
    "ichimoku_senkou_a_9_26_52",
    "ichimoku_senkou_b_9_26_52",
    "ichimoku_chikou_26",
)


def upgrade() -> None:
    for column in ADVANCED_COLUMNS:
        op.execute(f"""
            DO $$
            BEGIN
                IF to_regclass('public.market_indicator') IS NOT NULL THEN
                    ALTER TABLE market_indicator ADD COLUMN IF NOT EXISTS {column} NUMERIC;
                END IF;
            END $$;
            """)


def downgrade() -> None:
    for column in reversed(ADVANCED_COLUMNS):
        op.execute(f"""
            DO $$
            BEGIN
                IF to_regclass('public.market_indicator') IS NOT NULL THEN
                    ALTER TABLE market_indicator DROP COLUMN IF EXISTS {column};
                END IF;
            END $$;
            """)
