"""Card #1117: a migração Alembic cria o catálogo e o ledger de atualização."""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from app.models_asset_catalog import AssetCatalog, AssetCatalogRefresh

MIGRATION = Path(__file__).parents[2] / "alembic/versions/20261020_0001_asset_catalog.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("migration_1117", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_matches_models_and_is_reversible_in_a_private_schema(unit_database_url):
    module = _load_migration()
    assert module.down_revision == "20261013_0001"
    engine = create_engine(unit_database_url)
    schema = "migration_1117_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            context = MigrationContext.configure(conn)
            with Operations.context(context):
                module.upgrade()
            inspector = inspect(conn)
            tables = set(inspector.get_table_names(schema=schema))
            assert {"asset_catalog", "asset_catalog_refresh"} <= tables
            for model in (AssetCatalog, AssetCatalogRefresh):
                created = {
                    c["name"] for c in inspector.get_columns(model.__tablename__, schema=schema)
                }
                assert created == {c.name for c in model.__table__.columns}, model.__tablename__
            conn.execute(
                text(
                    "INSERT INTO asset_catalog (asset_id, asset_class, symbol, state, first_seen_at, last_seen_at) "
                    "VALUES ('binance:spot:BTC/USDT', 'crypto', 'BTC/USDT', 'tradable', now(), now())"
                )
            )
            with Operations.context(context):
                module.downgrade()
            assert not {"asset_catalog", "asset_catalog_refresh"} & set(
                inspect(conn).get_table_names(schema=schema)
            )
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()
