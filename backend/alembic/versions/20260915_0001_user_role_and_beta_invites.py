"""Persist the administrator role and add single-use beta invites (#689).

Revision ID: 20260915_0001
Revises: 20260909_0001
Create Date: 2026-09-15 12:00:00

Deploy order contract (D9): the host bootstrap command runs **before** this
migration, and the route enforcement runs **after** it.  The backfill below
promotes only an ``ADMIN_EMAILS`` address that already owns an account; it
never creates an account, so the configured admin of a fresh deployment is
created explicitly by ``ops/bootstrap_admin.py``.
"""

from __future__ import annotations

import os

import sqlalchemy as sa
from alembic import op

revision = "20260915_0001"
down_revision = "20260909_0001"
branch_labels = None
depends_on = None

USERS_TABLE = "users"
BETA_INVITES_TABLE = "beta_invites"


def _configured_admin_emails() -> list[str]:
    raw = os.getenv("ADMIN_EMAILS", "") or ""
    ordered = [email.strip().lower() for email in raw.split(",") if email.strip()]
    return list(dict.fromkeys(ordered))


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    if not _has_table(table_name):
        return False
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _backfill_admin_role() -> None:
    """Promote the already-configured admin when that account already exists."""

    if not _has_column(USERS_TABLE, "role"):
        return

    bind = op.get_bind()
    statement = sa.text(
        "UPDATE users SET role = 'admin' WHERE lower(email) = :email AND role <> 'admin'"
    )
    for email in _configured_admin_emails():
        bind.execute(statement, {"email": email})


def upgrade() -> None:
    if _has_table(USERS_TABLE) and not _has_column(USERS_TABLE, "role"):
        op.add_column(
            USERS_TABLE,
            sa.Column(
                "role",
                sa.String(length=16),
                nullable=False,
                server_default="user",
            ),
        )

    if not _has_table(BETA_INVITES_TABLE):
        op.create_table(
            BETA_INVITES_TABLE,
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("token_hash", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_by_user_id", sa.String(), nullable=True),
            sa.Column("consumed_at", sa.DateTime(), nullable=True),
            sa.Column("consumed_user_id", sa.String(), nullable=True),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("revoked_reason", sa.String(), nullable=True),
            sa.Column("superseded_by_id", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_beta_invites_email", BETA_INVITES_TABLE, ["email"], unique=False)
        op.create_index(
            "ix_beta_invites_token_hash",
            BETA_INVITES_TABLE,
            ["token_hash"],
            unique=True,
        )
        op.create_index(
            "ix_beta_invites_email_created_at",
            BETA_INVITES_TABLE,
            ["email", "created_at"],
            unique=False,
        )

    _backfill_admin_role()


def downgrade() -> None:
    # Reversible: the invite table and the role column are dropped.  The role
    # backfill is intentionally not "undone" by writing role='user' back to the
    # promoted admin -- that would risk locking the configured admin out and is
    # not a safe automatic reversal.
    if _has_table(BETA_INVITES_TABLE):
        op.drop_index("ix_beta_invites_email_created_at", table_name=BETA_INVITES_TABLE)
        op.drop_index("ix_beta_invites_token_hash", table_name=BETA_INVITES_TABLE)
        op.drop_index("ix_beta_invites_email", table_name=BETA_INVITES_TABLE)
        op.drop_table(BETA_INVITES_TABLE)

    if _has_column(USERS_TABLE, "role"):
        op.drop_column(USERS_TABLE, "role")
