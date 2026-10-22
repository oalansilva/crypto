"""Add the persisted Binance asset catalog and its refresh ledger (#1117)."""

from alembic import op
import sqlalchemy as sa

revision = "20261020_0001"
down_revision = "20261013_0001"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade():
    # O app também cria as tabelas na subida (create_all); a migração é idempotente.
    if _has_table("asset_catalog") and _has_table("asset_catalog_refresh"):
        return
    op.create_table(
        "asset_catalog",
        sa.Column("asset_id", sa.String(96), primary_key=True),
        sa.Column("asset_class", sa.String(16), nullable=False),
        sa.Column("symbol", sa.String(64), nullable=False),
        sa.Column("name", sa.String(300), nullable=False, server_default=""),
        sa.Column("binance_id", sa.String(96), nullable=False, server_default=""),
        sa.Column("state", sa.String(24), nullable=False),
        sa.Column("state_reason", sa.String(300)),
        sa.Column("info_note", sa.String(300)),
        sa.Column("search_key", sa.Text(), nullable=False, server_default=""),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True)),
        sa.Column("history_from", sa.DateTime(timezone=True)),
        sa.Column("history_to", sa.DateTime(timezone=True)),
        sa.Column("history_checked_at", sa.DateTime(timezone=True)),
        sa.Column("extra", sa.JSON()),
    )
    op.create_index("ix_asset_catalog_class_symbol", "asset_catalog", ["asset_class", "symbol"])
    op.create_index("ix_asset_catalog_symbol", "asset_catalog", ["symbol"])
    op.create_index("ix_asset_catalog_class_state", "asset_catalog", ["asset_class", "state"])

    op.create_table(
        "asset_catalog_refresh",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("catalog_group", sa.String(16), nullable=False),
        sa.Column("trigger", sa.String(16), nullable=False, server_default="scheduled"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("error_code", sa.String(64)),
        sa.Column("error_message", sa.Text()),
        sa.Column("counts", sa.JSON()),
    )
    op.create_index(
        "ix_asset_catalog_refresh_group_started",
        "asset_catalog_refresh",
        ["catalog_group", "started_at"],
    )


def downgrade():
    # Rollback leaves the tables unread by the application; favorites and
    # results never reference them, so dropping is safe but not required.
    op.drop_index("ix_asset_catalog_refresh_group_started", table_name="asset_catalog_refresh")
    op.drop_table("asset_catalog_refresh")
    op.drop_index("ix_asset_catalog_class_state", table_name="asset_catalog")
    op.drop_index("ix_asset_catalog_symbol", table_name="asset_catalog")
    op.drop_index("ix_asset_catalog_class_symbol", table_name="asset_catalog")
    op.drop_table("asset_catalog")
