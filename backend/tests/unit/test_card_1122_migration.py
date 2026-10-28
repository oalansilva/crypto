"""Card #1122: migração da identidade do favorito, das marcas "Alertar" e do estado por favorito."""

from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

import pytest

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


# ---------------------------------------------------------------- 20261027_0001 (Design d2)

MIGRATION_D2 = (
    Path(__file__).parents[2] / "alembic/versions/20261027_0001_monitor_alert_on_by_default.py"
)

POST_1122 = [
    """CREATE TABLE favorite_strategies (
        id SERIAL PRIMARY KEY, user_id VARCHAR, name VARCHAR NOT NULL, symbol VARCHAR NOT NULL,
        timeframe VARCHAR NOT NULL, strategy_name VARCHAR NOT NULL, parameters TEXT NOT NULL,
        notes VARCHAR, tier INTEGER, notify_telegram BOOLEAN NOT NULL DEFAULT FALSE
    )""",
    """CREATE TABLE monitor_observed_statuses (
        id SERIAL PRIMARY KEY, symbol VARCHAR NOT NULL, timeframe VARCHAR NOT NULL,
        status VARCHAR NOT NULL, observed_at TIMESTAMP NOT NULL DEFAULT now(),
        opportunity_id VARCHAR, payload_json TEXT
    )""",
    """CREATE TABLE monitor_favorite_alert_states (
        favorite_id INTEGER PRIMARY KEY REFERENCES favorite_strategies(id) ON DELETE CASCADE,
        status VARCHAR NOT NULL, candle_time VARCHAR, observed_at TIMESTAMP NOT NULL,
        payload_json TEXT
    )""",
]


def _load_d2_migration():
    spec = importlib.util.spec_from_file_location("migration_1122_d2", MIGRATION_D2)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_d2_migration_removes_auto_star_switches_alerts_on_and_seeds_state(
    unit_database_url, monkeypatch
):
    monkeypatch.delenv("MONITOR_TELEGRAM_TIER_FILTER", raising=False)
    module = _load_d2_migration()
    assert (module.revision, module.down_revision) == ("20261027_0001", "20261026_0001")
    engine = create_engine(unit_database_url)
    schema = "migration_1122_d2_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            for statement in POST_1122:
                conn.execute(text(statement))
            rows = [
                # (id, símbolo, nota, estrelas, alerta)
                (1, "QQQ", "gerado em lote (7f3c2a91)", 3, False),  # estrela automática: sai
                (2, "SPY", "gerado em lote (7f3c2a91)", 2, False),  # subida pela pessoa: fica
                (3, "BTC/USDT", "descoberta via sweep sw-1 (result RS-1)", 3, True),  # sai
                (4, "ETH/USDT", "descoberta via sweep sw-2 (result RS-2)", 1, False),  # fica
                (5, "NVDA", None, 3, False),  # favorito manual com 1 estrela: fica
                (6, "AAPL", "minha nota", None, False),  # sem estrela: fica sem estrela
                (7, "SOL/USDT", None, 1, True),  # já tem estado: não é semeado de novo
            ]
            for fid, symbol, notes, tier, notify in rows:
                conn.execute(
                    text(
                        "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, "
                        "strategy_name, parameters, notes, tier, notify_telegram) VALUES "
                        "(:id, 'admin-1', :name, :symbol, '1d', 'multi_ma_crossover', '{}', "
                        ":notes, :tier, :notify)"
                    ),
                    {
                        "id": fid,
                        "name": f"fav {fid}",
                        "symbol": symbol,
                        "notes": notes,
                        "tier": tier,
                        "notify": notify,
                    },
                )
            conn.execute(
                text(
                    "INSERT INTO monitor_observed_statuses (symbol, timeframe, status) VALUES "
                    "('SPY', '1d', 'HOLD'), ('NVDA', '1d', 'EXIT'), ('QQQ', '1d', 'HOLD'), "
                    "('SOL/USDT', '1d', 'EXIT'), ('AAPL', '1d', 'HOLD')"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO monitor_favorite_alert_states (favorite_id, status, observed_at) "
                    "VALUES (7, 'HOLD', now())"
                )
            )

            context = MigrationContext.configure(conn)
            with Operations.context(context):
                module.upgrade()

            after = {
                r.id: (r.tier, r.notify_telegram)
                for r in conn.execute(
                    text("SELECT id, tier, notify_telegram FROM favorite_strategies")
                )
            }
            # d2-1: só a 1 estrela automática de lote/Descoberta sai; d2-2: todos com alerta ligado.
            assert after == {
                1: (None, True),
                2: (2, True),
                3: (None, True),
                4: (1, True),
                5: (3, True),
                6: (None, True),
                7: (1, True),
            }
            states = dict(
                conn.execute(
                    text("SELECT favorite_id, status FROM monitor_favorite_alert_states")
                ).fetchall()
            )
            # Semente só para quem passa a alertar (com estrela) e ainda não tinha estado.
            assert states == {2: "HOLD", 5: "EXIT", 7: "HOLD"}
            # Default novo: favorito sem valor explícito nasce com o alerta ligado.
            conn.execute(
                text(
                    "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, "
                    "strategy_name, parameters) VALUES (99, 'u', 'novo', 'SPY', '1d', 'x', '{}')"
                )
            )
            assert (
                conn.execute(
                    text("SELECT notify_telegram FROM favorite_strategies WHERE id = 99")
                ).scalar()
                is True
            )

            with Operations.context(context):
                module.downgrade()
            # Downgrade: só o default volta; os dados mudados ficam.
            conn.execute(
                text(
                    "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, "
                    "strategy_name, parameters) VALUES (100, 'u', 'velho', 'SPY', '1d', 'x', '{}')"
                )
            )
            assert (
                conn.execute(
                    text("SELECT notify_telegram FROM favorite_strategies WHERE id = 100")
                ).scalar()
                is False
            )
            assert conn.execute(
                text("SELECT tier, notify_telegram FROM favorite_strategies WHERE id = 1")
            ).one() == (None, True)
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()


@pytest.mark.parametrize("source", ["preference", "env"])
def test_d2_migration_drops_stale_state_of_favorites_not_evaluated_before(
    unit_database_url, monkeypatch, source
):
    """Estado de favorito que a varredura anterior não avaliava não sobrevive à migração.

    Alerta desmarcado (o PATCH antigo não apagava o estado) ou fora do filtro de estrelas do
    sistema: o estado parado sai; o favorito é semeado do par observado ou fica sem estado (a
    primeira leitura é só base). Nenhum dos dois gera entrada/saída de uma mudança antiga.
    """

    module = _load_d2_migration()
    monkeypatch.delenv("MONITOR_TELEGRAM_TIER_FILTER", raising=False)
    if source == "env":
        monkeypatch.setenv("MONITOR_TELEGRAM_TIER_FILTER", "1,2")
    engine = create_engine(unit_database_url)
    schema = "migration_1122_d2s_" + uuid.uuid4().hex[:12]
    try:
        with engine.begin() as conn:
            conn.execute(text(f"CREATE SCHEMA {schema}"))
            conn.execute(text(f"SET LOCAL search_path TO {schema}"))
            for statement in POST_1122:
                conn.execute(text(statement))
            conn.execute(
                text(
                    "CREATE TABLE system_preferences (key VARCHAR PRIMARY KEY, value TEXT, "
                    "updated_at TIMESTAMP, updated_by_user_id VARCHAR)"
                )
            )
            if source == "preference":
                conn.execute(
                    text(
                        "INSERT INTO system_preferences (key, value) "
                        "VALUES ('monitor_telegram_tier_filter', '1,2')"
                    )
                )
            rows = [
                # (id, símbolo, estrelas, alerta) — todos com estado antigo "EXIT"
                (1, "SOL/USDT", 1, True),  # avaliado antes (no filtro, alerta ligado): fica
                (2, "MSFT", 2, False),  # alerta desmarcado: estado parado, semeado do par
                (3, "TSLA", 2, False),  # alerta desmarcado, sem par observado: sem estado
                (4, "IWM", 3, True),  # fora do filtro "1,2": estado parado, sem estado
            ]
            for fid, symbol, tier, notify in rows:
                conn.execute(
                    text(
                        "INSERT INTO favorite_strategies (id, user_id, name, symbol, timeframe, "
                        "strategy_name, parameters, tier, notify_telegram) VALUES "
                        "(:id, 'admin-1', :name, :symbol, '1d', 'multi_ma_crossover', '{}', "
                        ":tier, :notify)"
                    ),
                    {
                        "id": fid,
                        "name": f"fav {fid}",
                        "symbol": symbol,
                        "tier": tier,
                        "notify": notify,
                    },
                )
                conn.execute(
                    text(
                        "INSERT INTO monitor_favorite_alert_states "
                        "(favorite_id, status, observed_at, payload_json) "
                        "VALUES (:id, 'EXIT', now() - interval '20 days', :payload)"
                    ),
                    {"id": fid, "payload": json.dumps({"stale": True})},
                )
            conn.execute(
                text(
                    "INSERT INTO monitor_observed_statuses (symbol, timeframe, status) VALUES "
                    "('SOL/USDT', '1d', 'HOLD'), ('MSFT', '1d', 'HOLD')"
                )
            )

            context = MigrationContext.configure(conn)
            with Operations.context(context):
                module.upgrade()

            states = {
                r.favorite_id: (r.status, json.loads(r.payload_json or "null"))
                for r in conn.execute(
                    text(
                        "SELECT favorite_id, status, payload_json FROM monitor_favorite_alert_states"
                    )
                )
            }
            # Quem já era avaliado guarda a própria leitura (não volta para o par observado).
            assert states[1] == ("EXIT", {"stale": True})
            # Alerta desmarcado: o "EXIT" parado saiu; a base é a leitura do par ("HOLD").
            assert states[2] == ("HOLD", None)
            # Sem par observado (alerta desmarcado ou fora do filtro): sem estado, a primeira
            # leitura é só base.
            assert 3 not in states and 4 not in states
            assert set(states) == {1, 2}
            assert conn.execute(
                text("SELECT bool_and(notify_telegram) FROM favorite_strategies")
            ).scalar()
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        engine.dispose()
