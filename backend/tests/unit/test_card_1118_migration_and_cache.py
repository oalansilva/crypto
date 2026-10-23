"""Card #1118: revisão Alembic, migração da cripto e cache Parquet reconstruível."""

from __future__ import annotations

import importlib.util
import json
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from app.services.market_history import migration, store
from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.model import crypto_spec
from app.services.market_history.schema import (
    LEGACY_OHLCV_TABLE,
    LIVE_OHLCV_TABLE,
    STAGING_OHLCV_TABLE,
    execute_all,
    ohlcv_table_sql,
    side_table_statements,
)
from app.services.market_history.service import HistoryService
from market_history_support import FakeCcxt, crypto_frame

MIGRATION_FILE = Path(__file__).parents[2] / "alembic/versions/20261023_0001_market_history.py"

LEGACY_DDL = (
    """
    CREATE TABLE market_ohlcv (
        symbol TEXT NOT NULL, timeframe TEXT NOT NULL, candle_time TIMESTAMPTZ NOT NULL,
        open NUMERIC NOT NULL, high NUMERIC NOT NULL, low NUMERIC NOT NULL,
        close NUMERIC NOT NULL, volume NUMERIC NOT NULL, source TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        PRIMARY KEY (symbol, timeframe, candle_time, source))
    """,
    "CREATE UNIQUE INDEX uq_market_ohlcv_symbol_timeframe_candle_time ON market_ohlcv (symbol, timeframe, candle_time)",
    "CREATE INDEX idx_market_ohlcv_symbol_timeframe_time ON market_ohlcv (symbol, timeframe, candle_time DESC)",
    "CREATE INDEX idx_market_ohlcv_symbol_timeframe_source ON market_ohlcv (symbol, timeframe, source)",
)


def _load_revision():
    spec = importlib.util.spec_from_file_location("revision_1118", MIGRATION_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def raw_schema(unit_database_url):
    """Schema descartável SEM tabelas do histórico (estado antes da migração)."""

    admin = create_engine(unit_database_url)
    schema = "mig1118_" + uuid.uuid4().hex[:10]
    with admin.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
    engine = create_engine(unit_database_url, connect_args={"options": f"-csearch_path={schema}"})
    store.reset_table_cache()
    try:
        yield engine, schema
    finally:
        engine.dispose()
        store.reset_table_cache()
        with admin.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        admin.dispose()


def test_alembic_revision_creates_the_history_tables_is_idempotent_and_reversible(raw_schema):
    engine, schema = raw_schema
    module = _load_revision()
    assert module.down_revision == "20261020_0001" and module.revision == "20261023_0001"
    with engine.begin() as conn:
        for table in ("favorite_strategies", "auto_backtest_runs", "discovery_results"):
            conn.execute(text(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)"))
        for statement in LEGACY_DDL:
            conn.execute(text(statement))
        context = MigrationContext.configure(conn)
        with Operations.context(context):
            module.upgrade()
            module.upgrade()  # idempotente: o app também cria estas tabelas na subida
        inspector = inspect(conn)
        tables = set(inspector.get_table_names(schema=schema))
        assert {
            "market_series",
            "market_ohlcv_v2",
            "market_series_fetch",
            "market_series_coverage",
            "market_series_stage",
            "execution_data_snapshots",
            "market_rate_limit",
        } <= tables
        assert "market_ohlcv" in tables  # o legado não é tocado pela revisão
        key = inspector.get_pk_constraint("market_ohlcv_v2", schema=schema)["constrained_columns"]
        assert key == ["series_id", "candle_time"]
        assert "snapshot_id" in {
            c["name"] for c in inspector.get_columns("favorite_strategies", schema=schema)
        }
        assert "snapshot_id" in {
            c["name"] for c in inspector.get_columns("auto_backtest_runs", schema=schema)
        }
        provenance = {c["name"] for c in inspector.get_columns("discovery_results", schema=schema)}
        assert {
            "data_source",
            "asset_class",
            "session",
            "adjustment",
            "timeframe_origin",
            "period_requested",
            "period_covered",
            "data_version",
            "snapshot_id",
        } <= provenance
        # Sem a extensão Timescale (este banco), nenhuma política é criada e nada quebra.
        with Operations.context(context):
            module.downgrade()
        assert "market_series" not in set(inspect(conn).get_table_names(schema=schema))
        assert "market_ohlcv" in set(inspect(conn).get_table_names(schema=schema))


def test_alembic_downgrade_refuses_after_the_name_swap(raw_schema):
    engine, _ = raw_schema
    module = _load_revision()
    with engine.begin() as conn:
        execute_all(conn, side_table_statements())
        execute_all(conn, ohlcv_table_sql(LIVE_OHLCV_TABLE))  # tabela nova já com o nome definitivo
        context = MigrationContext.configure(conn)
        with Operations.context(context):
            with pytest.raises(RuntimeError, match="rollback"):
                module.downgrade()


def _seed_legacy(engine, frame: pd.DataFrame, symbol="BTC/USDT", timeframe="1h", source="ccxt"):
    rows = [
        {
            "s": symbol,
            "tf": timeframe,
            "t": ts.to_pydatetime(),
            "o": float(r.open),
            "h": float(r.high),
            "l": float(r.low),
            "c": float(r.close),
            "v": float(r.volume),
            "src": source,
        }
        for ts, r in frame.iterrows()
    ]
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO market_ohlcv (symbol, timeframe, candle_time, open, high, low, close, volume, source) "
                "VALUES (:s, :tf, :t, :o, :h, :l, :c, :v, :src)"
            ),
            rows,
        )


def _write_parquet(path: Path, frame: pd.DataFrame):
    out = frame.reset_index()
    out["timestamp"] = pd.DatetimeIndex(out["candle_time"]).as_unit("ms").asi8
    out["timestamp_utc"] = out["candle_time"]
    out.drop(columns=["candle_time"]).to_parquet(path, index=False)


@pytest.fixture
def migrated(raw_schema, tmp_path):
    engine, _ = raw_schema
    module = _load_revision()
    with engine.begin() as conn:
        for table in ("favorite_strategies", "auto_backtest_runs", "discovery_results"):
            conn.execute(text(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)"))
        for statement in LEGACY_DDL:
            conn.execute(text(statement))
        context = MigrationContext.configure(conn)
        with Operations.context(context):
            module.upgrade()
    return engine, tmp_path


def test_migration_copies_imports_only_what_is_missing_and_records_divergences(migrated):
    engine, tmp_path = migrated
    full = crypto_frame("2026-09-01", 300, "1h")
    legacy = full.iloc[100:]  # a tabela só tem os últimos candles (retenção antiga)
    _seed_legacy(engine, legacy)
    _seed_legacy(engine, crypto_frame("2026-09-01", 40, "1D"), timeframe="1d")
    parquet = full.copy()
    parquet.iloc[150, parquet.columns.get_loc("close")] += 3.0  # divergência entre as duas cópias
    parquet_dir = tmp_path / "binance"
    parquet_dir.mkdir()
    _write_parquet(parquet_dir / "BTC_USDT_1h.parquet", parquet)

    dry = migration.run_migration(engine, parquet_dir=parquet_dir, execute=False)
    assert not dry.swapped and {(s.symbol, s.timeframe) for s in dry.series} == {
        ("BTC/USDT", "1h"),
        ("BTC/USDT", "1d"),
    }
    with engine.connect() as conn:
        assert (
            conn.execute(text(f"SELECT count(*) FROM {STAGING_OHLCV_TABLE}")).scalar() == 0
        )  # ensaio não escreve

    report = migration.run_migration(engine, parquet_dir=parquet_dir, execute=True, swap=False)
    by_key = {(s.symbol, s.timeframe): s for s in report.series}
    hourly = by_key[("BTC/USDT", "1h")]
    assert hourly.copied == 200 and hourly.parquet_imported == 100
    assert hourly.divergences == 1 and hourly.compared == 200
    assert hourly.ok is False  # 1/200 acima de 0,01%: a chave não vira
    assert any("acima do limite" in p for p in hourly.problems)
    assert report.blocked and not report.swapped
    assert (
        report.divergences_sample[0]["table"]["close"]
        != report.divergences_sample[0]["parquet"]["close"]
    )
    with engine.connect() as conn:
        from app.services.market_history.schema import ohlcv_table_is_new_shape as _new_shape

        assert not _new_shape(conn)  # sem --swap o legado continua com o nome
        kept = conn.execute(
            text(
                f"SELECT close FROM {STAGING_OHLCV_TABLE} WHERE candle_time = :t AND series_id = :s"
            ),
            {"t": full.index[150].to_pydatetime(), "s": hourly.series_id},
        ).scalar()
    assert float(kept) == pytest.approx(
        float(legacy.loc[full.index[150], "close"])
    )  # vale a tabela


def test_migration_swaps_names_when_every_series_checks_out_and_can_roll_back(migrated):
    engine, tmp_path = migrated
    full = crypto_frame("2026-09-01", 300, "1h")
    _seed_legacy(engine, full.iloc[100:])
    _seed_legacy(engine, crypto_frame("2026-09-01", 40, "1D"), timeframe="1d")
    parquet_dir = tmp_path / "binance"
    parquet_dir.mkdir()
    _write_parquet(parquet_dir / "BTC_USDT_1h.parquet", full)

    report = migration.run_migration(engine, parquet_dir=parquet_dir, execute=True, swap=True)
    assert report.swapped and not report.blocked
    assert all(s.ok for s in report.series)
    daily = [s for s in report.series if s.timeframe == "1d"][0]
    assert daily.close_sum_actual == pytest.approx(daily.close_sum_expected)

    from app.services.market_history.schema import ohlcv_table_is_new_shape, has_table

    with engine.connect() as conn:
        assert ohlcv_table_is_new_shape(conn, LIVE_OHLCV_TABLE)
        assert has_table(conn, LEGACY_OHLCV_TABLE) and not has_table(conn, STAGING_OHLCV_TABLE)
    service = HistoryService(engine, update_ttl_seconds=0)
    series = service.resolve(crypto_spec("BTC/USDT", "1h"))
    result = service.read(series)
    assert len(result.candles) == 300 and result.coverage["gap_count"] == 0
    np.testing.assert_allclose(
        result.candles["close"].to_numpy(), full["close"].to_numpy(), rtol=1e-12
    )
    assert result.coverage["covered"]["start"].startswith("2026-09-01")

    # Segunda execução é um no-op seguro.
    again = migration.run_migration(engine, parquet_dir=parquet_dir, execute=True, swap=True)
    assert again.blocked and not again.swapped

    migration.rollback_swap(engine)
    with engine.connect() as conn:
        assert not ohlcv_table_is_new_shape(conn, LIVE_OHLCV_TABLE)
        assert conn.execute(text("SELECT count(*) FROM market_ohlcv")).scalar() == 200 + 40
        assert has_table(conn, STAGING_OHLCV_TABLE)


def test_repeating_execute_before_the_swap_still_checks_out(migrated):
    """Roteiro do operador: ``--execute`` e depois ``--execute --swap`` (idempotente, sem falso alarme)."""

    engine, tmp_path = migrated
    full = crypto_frame("2026-09-01", 300, "1h")
    _seed_legacy(engine, full.iloc[100:])
    parquet_dir = tmp_path / "binance"
    parquet_dir.mkdir()
    _write_parquet(parquet_dir / "BTC_USDT_1h.parquet", full)

    first = migration.run_migration(engine, parquet_dir=parquet_dir, execute=True, swap=False)
    assert [s.parquet_imported for s in first.series] == [100] and all(s.ok for s in first.series)
    second = migration.run_migration(engine, parquet_dir=parquet_dir, execute=True, swap=True)
    assert [s.parquet_imported for s in second.series] == [0]  # nada novo para importar
    assert all(s.ok for s in second.series), [s.problems for s in second.series]
    assert second.swapped and not second.blocked
    series = second.series[0]
    assert series.close_sum_actual == pytest.approx(series.close_sum_expected)


def test_migration_keeps_legacy_provider_candles_out_of_the_binance_series(migrated):
    engine, tmp_path = migrated
    _seed_legacy(
        engine, crypto_frame("2026-09-01", 30, "1D"), symbol="AAPL", timeframe="1d", source="stooq"
    )
    _seed_legacy(engine, crypto_frame("2026-09-01", 30, "1D"), symbol="BTC/USDT", timeframe="1d")
    report = migration.run_migration(engine, parquet_dir=None, execute=True, swap=True)
    assert report.swapped
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT asset_id, source FROM market_series ORDER BY asset_id")
        ).all()
    assert [(r[0], r[1]) for r in rows] == [
        ("binance:spot:BTC/USDT", "binance_spot"),
        ("legacy:stooq:AAPL", "stooq"),
    ]


# --- cache Parquet derivado --------------------------------------------------


@pytest.fixture
def history(unit_database_url, tmp_path):
    from market_history_support import history_schema

    with history_schema(unit_database_url) as engine:
        frame = crypto_frame("2026-10-01", 24 * 12, "1h")
        ccxt = FakeCcxt({("BTC/USDT", "1h"): frame})
        service = HistoryService(engine, ccxt_client=ccxt, update_ttl_seconds=0)
        series = service.resolve(crypto_spec("BTC/USDT", "1h"))
        service.ensure(series, "2026-10-01")
        yield service, series, ccxt, ParquetReadCache(tmp_path / "series")


def test_cache_is_rebuilt_from_postgres_without_calling_the_exchange(history, tmp_path):
    service, series, ccxt, cache = history
    first = cache.read(service, series, "2026-10-02", "2026-10-06")
    path = cache.path(series)
    assert path.exists() and (path.parent.parent.name == str(series.series_id))
    assert path.parent.name == "v1" and path.name == "1h.parquet"
    calls = len(ccxt.calls)
    import shutil

    shutil.rmtree(cache.root)  # apagar o cache não perde histórico
    again = cache.read(service, series, "2026-10-02", "2026-10-06")
    assert len(ccxt.calls) == calls  # nenhuma chamada à exchange
    pd.testing.assert_frame_equal(first, again, check_exact=True)
    full = service.read(series).candles
    assert len(full) == 24 * 12  # nada se perdeu no PostgreSQL
    pd.testing.assert_frame_equal(cache.read(service, series), full, check_exact=True)


def test_cache_follows_new_candles_and_new_versions(history):
    service, series, ccxt, cache = history
    cache.read(service, series)
    v1_path = cache.path(series)
    meta_before = json.loads(v1_path.with_suffix(".meta.json").read_text())
    # candle novo: o cache da mesma versão é refeito (marca do conteúdo mudou)
    ccxt.frames[("BTC/USDT", "1h")] = crypto_frame("2026-10-01", 24 * 12 + 5, "1h")
    service.ensure(series, "2026-10-01", force_update=True)
    assert len(cache.read(service, series)) == 24 * 12 + 5
    assert json.loads(v1_path.with_suffix(".meta.json").read_text()) != meta_before
    # correção de candle antigo: versão nova = arquivo novo; o antigo some
    corrected = crypto_frame("2026-10-01", 24 * 12 + 5, "1h")
    corrected.iloc[-3, corrected.columns.get_loc("close")] += 9
    ccxt.frames[("BTC/USDT", "1h")] = corrected
    service.ensure(series, "2026-10-01", force_update=True)
    fresh = service.read(series).series
    assert fresh.data_version == 2
    cache.read(service, fresh)
    assert cache.path(fresh).exists() and cache.path(fresh).parent.name == "v2"
    assert not v1_path.exists()


def test_cache_respects_the_size_ceiling_by_last_access(history, tmp_path):
    service, series, ccxt, _ = history
    tiny = ParquetReadCache(tmp_path / "tiny", max_bytes=1)
    other = service.resolve(crypto_spec("ETH/USDT", "1h"))
    ccxt.frames[("ETH/USDT", "1h")] = crypto_frame("2026-10-01", 48, "1h")
    service.ensure(other, "2026-10-01")
    tiny.read(service, series)
    tiny.read(service, other)
    survivors = [p for p in tiny.root.rglob("*.parquet")]
    assert len(survivors) == 1  # o mais recente fica; o resto sai para caber no teto
