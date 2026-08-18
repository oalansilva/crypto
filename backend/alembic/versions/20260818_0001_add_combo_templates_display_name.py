"""Add display_name to combo_templates for public identity overrides."""

from alembic import op

revision = "20260818_0001"
down_revision = "20260814_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.combo_templates') IS NOT NULL THEN
                ALTER TABLE combo_templates
                    ADD COLUMN IF NOT EXISTS display_name VARCHAR NULL;
            END IF;
        END $$;
        """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF to_regclass('public.combo_templates') IS NOT NULL THEN
                ALTER TABLE combo_templates
                    DROP COLUMN IF EXISTS display_name;
            END IF;
        END $$;
        """)
