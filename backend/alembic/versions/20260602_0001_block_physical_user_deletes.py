"""Block physical user deletes in runtime.

Revision ID: 20260602_0001
Revises: 20260519_0001
Create Date: 2026-06-02 03:30:00
"""

from __future__ import annotations

from alembic import op

revision = "20260602_0001"
down_revision = "20260519_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.block_physical_users_delete()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RAISE EXCEPTION
            'physical deletion/truncate from public.users is blocked in runtime; use status/is_banned or explicit audited maintenance instead';
        END;
        $$;
        """
    )
    op.execute("DROP TRIGGER IF EXISTS trg_block_users_delete ON public.users;")
    op.execute("DROP TRIGGER IF EXISTS trg_block_users_truncate ON public.users;")
    op.execute(
        """
        CREATE TRIGGER trg_block_users_delete
        BEFORE DELETE ON public.users
        FOR EACH STATEMENT
        EXECUTE FUNCTION public.block_physical_users_delete();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_block_users_truncate
        BEFORE TRUNCATE ON public.users
        FOR EACH STATEMENT
        EXECUTE FUNCTION public.block_physical_users_delete();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_block_users_delete ON public.users;")
    op.execute("DROP TRIGGER IF EXISTS trg_block_users_truncate ON public.users;")
    op.execute("DROP FUNCTION IF EXISTS public.block_physical_users_delete();")
