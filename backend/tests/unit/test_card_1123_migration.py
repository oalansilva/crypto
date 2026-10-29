"""Card #1123: migração da comparação gravada (tabelas novas e ponteiro do favorito, sem backfill)."""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

MIGRATION = Path(__file__).parents[2] / "alembic/versions/20261028_0001_benchmark_comparisons.py"


def _load():
    spec = importlib.util.spec_from_file_location("migration_1123", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_creates_tables_and_pointer_without_backfill(unit_database_url):
    module = _load()
    assert module.down_revision == "20261026_0001"
    engine = create_engine(unit_database_url)
    schema = "migration_1123_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            conn.execute(
                text(
                    "CREATE TABLE favorite_strategies (id SERIAL PRIMARY KEY, user_id VARCHAR, "
                    "name VARCHAR NOT NULL, symbol VARCHAR NOT NULL)"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO favorite_strategies (user_id, name, symbol) VALUES ('u', 'BTC', 'BTC/USDT')"
                )
            )
            for _ in range(2):  # idempotente: o app também cria na subida
                context = MigrationContext.configure(conn)
                with Operations.context(context):
                    module.upgrade()
            insp = inspect(conn)
            tables = set(insp.get_table_names(schema=schema))
            assert {"benchmark_comparisons", "discovery_reference_columns"} <= tables
            columns = {c["name"] for c in insp.get_columns("favorite_strategies", schema=schema)}
            assert "benchmark_comparison_id" in columns
            assert (
                conn.execute(
                    text("SELECT benchmark_comparison_id FROM favorite_strategies")
                ).scalar()
                is None
            )
            fks = [
                fk
                for fk in insp.get_foreign_keys("favorite_strategies", schema=schema)
                if fk["constrained_columns"] == ["benchmark_comparison_id"]
            ]
            # Uma FK só, mesmo com a migração rodando duas vezes, e com ON DELETE SET NULL.
            assert len(fks) == 1 and fks[0]["referred_table"] == "benchmark_comparisons"
            assert fks[0]["name"] == "fk_favorite_strategies_benchmark_comparison"
            assert (fks[0].get("options") or {}).get("ondelete") == "SET NULL"
            _assert_set_null(conn)
            indexes = {
                i["name"] for i in insp.get_indexes("discovery_reference_columns", schema=schema)
            }
            assert "uq_discovery_reference_columns_active" in indexes
            conn.execute(
                text(
                    "INSERT INTO discovery_reference_columns (id, sweep_id, actor, reference, status, "
                    "active, created_at) VALUES ('a', 's', 'u', '{}', 'done', TRUE, now()), "
                    "('b', 's', 'u', '{}', 'done', FALSE, now())"
                )
            )
            try:
                with conn.begin_nested():
                    conn.execute(
                        text(
                            "INSERT INTO discovery_reference_columns (id, sweep_id, actor, reference, "
                            "status, active, created_at) VALUES ('c', 's', 'u', '{}', 'done', TRUE, now())"
                        )
                    )
                raise AssertionError("duas colunas ativas na mesma varredura e usuário")
            except Exception as exc:  # única ativa por (sweep, actor)
                assert "uq_discovery_reference_columns_active" in str(exc)
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        engine.dispose()


def _assert_set_null(conn):
    """Apagar a comparação deixa o ponteiro do favorito nulo (ON DELETE SET NULL)."""

    conn.execute(
        text(
            "INSERT INTO benchmark_comparisons (id, owner_kind, created_at, status, payload) "
            "VALUES ('cmp-fk', 'favorite', now(), 'valid', '{}')"
        )
    )
    conn.execute(text("UPDATE favorite_strategies SET benchmark_comparison_id = 'cmp-fk'"))
    conn.execute(text("DELETE FROM benchmark_comparisons WHERE id = 'cmp-fk'"))
    assert (
        conn.execute(text("SELECT benchmark_comparison_id FROM favorite_strategies")).scalar()
        is None
    )


def test_runtime_schema_sql_adds_the_pointer():
    from app.database import BENCHMARK_SCHEMA_SQL

    assert any("benchmark_comparison_id" in s for s in BENCHMARK_SCHEMA_SQL)


def test_runtime_schema_sql_adds_the_foreign_key_idempotently(unit_database_url):
    from app.database import BENCHMARK_SCHEMA_SQL

    engine = create_engine(unit_database_url)
    schema = "runtime_1123_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            conn.execute(
                text(
                    "CREATE TABLE favorite_strategies (id SERIAL PRIMARY KEY, user_id VARCHAR, "
                    "name VARCHAR NOT NULL, symbol VARCHAR NOT NULL)"
                )
            )
            # Sem a tabela das comparações ainda: só a coluna e o índice, sem FK e sem erro.
            for statement in BENCHMARK_SCHEMA_SQL:
                conn.execute(text(statement))
            insp = inspect(conn)
            assert insp.get_foreign_keys("favorite_strategies", schema=schema) == []
            conn.execute(
                text(
                    "CREATE TABLE benchmark_comparisons (id VARCHAR(36) PRIMARY KEY, "
                    "owner_kind VARCHAR(24) NOT NULL, created_at TIMESTAMP NOT NULL, "
                    "status VARCHAR(16) NOT NULL, payload JSON NOT NULL)"
                )
            )
            # Ponteiro órfão de antes da FK vira nulo em vez de quebrar a subida.
            conn.execute(
                text(
                    "INSERT INTO favorite_strategies (user_id, name, symbol, "
                    "benchmark_comparison_id) VALUES ('u', 'BTC', 'BTC/USDT', 'sumiu')"
                )
            )
            for _ in range(2):
                for statement in BENCHMARK_SCHEMA_SQL:
                    conn.execute(text(statement))
            fks = inspect(conn).get_foreign_keys("favorite_strategies", schema=schema)
            assert len(fks) == 1
            assert fks[0]["name"] == "fk_favorite_strategies_benchmark_comparison"
            assert fks[0]["referred_table"] == "benchmark_comparisons"
            assert (fks[0].get("options") or {}).get("ondelete") == "SET NULL"
            assert (
                conn.execute(
                    text("SELECT benchmark_comparison_id FROM favorite_strategies")
                ).scalar()
                is None
            )
            _assert_set_null(conn)
    finally:
        with engine.begin() as conn:
            conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
        engine.dispose()


def test_model_declares_the_same_foreign_key():
    from app.models import FavoriteStrategy

    (fk,) = FavoriteStrategy.__table__.c.benchmark_comparison_id.foreign_keys
    assert fk.target_fullname == "benchmark_comparisons.id"
    assert fk.ondelete == "SET NULL"
    assert fk.name == "fk_favorite_strategies_benchmark_comparison"
