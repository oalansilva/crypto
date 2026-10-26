"""Card #1122: migração da identidade do favorito, das marcas "Alertar" e do estado por favorito."""

from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

MIGRATION = Path(__file__).parents[2] / "alembic/versions/20261026_0001_favorite_alert_identity.py"


def _load_migration():
    spec = importlib.util.spec_from_file_location("migration_1122", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PRE_1122 = [
    """CREATE TABLE users (
        id VARCHAR PRIMARY KEY, email VARCHAR NOT NULL, role VARCHAR NOT NULL DEFAULT 'user'
    )""",
    """CREATE TABLE favorite_strategies (
        id SERIAL PRIMARY KEY, user_id VARCHAR, name VARCHAR NOT NULL, symbol VARCHAR NOT NULL,
        timeframe VARCHAR NOT NULL, strategy_name VARCHAR NOT NULL, parameters TEXT NOT NULL,
        metrics TEXT, tier INTEGER, notify_telegram BOOLEAN NOT NULL DEFAULT TRUE
    )""",
    """CREATE TABLE monitor_observed_statuses (
        id SERIAL PRIMARY KEY, symbol VARCHAR NOT NULL, timeframe VARCHAR NOT NULL,
        status VARCHAR NOT NULL, observed_at TIMESTAMP NOT NULL DEFAULT now(),
        opportunity_id VARCHAR, payload_json TEXT
    )""",
    """CREATE TABLE monitor_telegram_alerts (
        id SERIAL PRIMARY KEY, created_at TIMESTAMP NOT NULL DEFAULT now(), user_id VARCHAR,
        symbol VARCHAR NOT NULL, timeframe VARCHAR NOT NULL, previous_status VARCHAR,
        new_status VARCHAR NOT NULL, severity VARCHAR NOT NULL, destination_chat_id VARCHAR,
        destination_thread_id VARCHAR, result_status VARCHAR NOT NULL, error_text TEXT,
        payload_hash VARCHAR NOT NULL, source VARCHAR NOT NULL DEFAULT 'monitor', payload_json TEXT
    )""",
    """CREATE TABLE system_preferences (
        key VARCHAR PRIMARY KEY, value TEXT, updated_at TIMESTAMP, updated_by_user_id VARCHAR
    )""",
]


def _insert_favorite(conn, fid, user, symbol, parameters, metrics=None, notify=True):
    conn.execute(
        text(
            "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, strategy_name, "
            "parameters, metrics, notify_telegram) VALUES (:id, :user, :name, :symbol, '1d', "
            "'multi_ma_crossover', :parameters, :metrics, :notify)"
        ),
        {
            "id": fid,
            "user": user,
            "name": f"fav {fid}",
            "symbol": symbol,
            "parameters": json.dumps(parameters),
            "metrics": json.dumps(metrics or {}),
            "notify": notify,
        },
    )


def test_migration_backfills_configuration_clears_marks_and_seeds_state(
    unit_database_url, monkeypatch
):
    monkeypatch.setenv("ADMIN_EMAILS", "alan@test.local")
    module = _load_migration()
    assert module.down_revision == "20261025_0001"
    engine = create_engine(unit_database_url)
    schema = "migration_1122_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            for statement in PRE_1122:
                conn.execute(text(statement))
            conn.execute(
                text(
                    "INSERT INTO users (id, email, role) VALUES "
                    "('admin-1', 'alan@test.local', 'user'), ('user-1', 'bia@test.local', 'user')"
                )
            )
            _insert_favorite(conn, 1, "admin-1", "BTC/USDT", {"direction": "long"})
            _insert_favorite(
                conn,
                2,
                "user-1",
                "NVDA",
                {"direction": "long", "data_source": "binance_equity"},
                {"analysis_conventions": {"adjusted_prices": True}},
            )
            _insert_favorite(conn, 3, "user-1", "AAPL", {"direction": "long"})
            _insert_favorite(conn, 4, "user-1", "ETH/USDT", {"direction": "long"})
            conn.execute(
                text(
                    "INSERT INTO monitor_observed_statuses (symbol, timeframe, status) VALUES "
                    "('BTC/USDT', '1d', 'HOLD'), ('ETH/USDT', '1d', 'EXIT')"
                )
            )

            context = MigrationContext.configure(conn)
            with Operations.context(context):
                module.upgrade()

            rows = {
                r.id: r
                for r in conn.execute(
                    text(
                        "SELECT id, data_source, session, adjustment, notify_telegram "
                        "FROM favorite_strategies"
                    )
                )
            }
            assert (rows[1].data_source, rows[1].session, rows[1].adjustment) == (
                "ccxt",
                "24x7",
                "none",
            )
            assert (rows[2].data_source, rows[2].session, rows[2].adjustment) == (
                "binance_equity",
                "regular_ny",
                "split",
            )
            assert (rows[3].data_source, rows[3].session, rows[3].adjustment) == (
                "stooq",
                "eod",
                "legacy",
            )
            # Marca do admin fica; as de quem não é admin vão para falso.
            assert rows[1].notify_telegram is True
            assert not any(rows[i].notify_telegram for i in (2, 3, 4))
            # Estado semeado do par só para o favorito marcado (BTC do admin).
            states = conn.execute(
                text("SELECT favorite_id, status FROM monitor_favorite_alert_states")
            ).fetchall()
            assert [(s.favorite_id, s.status) for s in states] == [(1, "HOLD")]
            # Default novo: favorito sem marca explícita nasce sem "Alertar".
            conn.execute(
                text(
                    "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, "
                    "strategy_name, parameters) "
                    "VALUES (99, 'user-1', 'novo', 'SPY', '1d', 'x', '{}')"
                )
            )
            fresh = conn.execute(
                text("SELECT notify_telegram FROM favorite_strategies WHERE name = 'novo'")
            ).scalar()
            assert fresh is False
            inspector = inspect(conn)
            assert {"monitor_favorite_alert_states", "monitor_data_health"} <= set(
                inspector.get_table_names(schema=schema)
            )
            columns = {
                c["name"] for c in inspector.get_columns("monitor_telegram_alerts", schema=schema)
            }
            assert {"favorite_id", "event_key"} <= columns
            indexes = {
                i["name"] for i in inspector.get_indexes("monitor_telegram_alerts", schema=schema)
            }
            assert "ix_monitor_telegram_alerts_event_key_reserved" in indexes
            origin = conn.execute(
                text(
                    "SELECT value FROM system_preferences "
                    "WHERE key = 'monitor_telegram_favorite_origin_at'"
                )
            ).scalar()
            assert origin
            # Apagar o favorito apaga o estado (ON DELETE CASCADE).
            conn.execute(text("DELETE FROM favorite_strategies WHERE id = 1"))
            assert (
                conn.execute(text("SELECT count(*) FROM monitor_favorite_alert_states")).scalar()
                == 0
            )

            with Operations.context(context):
                module.downgrade()
            after = set(inspect(conn).get_table_names(schema=schema))
            assert not {"monitor_favorite_alert_states", "monitor_data_health"} & after
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()
