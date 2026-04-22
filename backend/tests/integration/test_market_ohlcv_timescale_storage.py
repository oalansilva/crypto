from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

import app.database as database_module
import app.services.ohlcv_storage as ohlcv_storage

_RETENTION_DSN_ENV = "MARKET_OHLCV_TEST_DSN"
_PERF_ENFORCE_ENV = "MARKET_OHLCV_PERF_TESTS"


def _build_test_engine():
    dsn = os.getenv(_RETENTION_DSN_ENV)
    if not dsn:
        pytest.skip(f"Set {_RETENTION_DSN_ENV} to run Timescale integration checks.")

    try:
        engine = create_engine(dsn)
    except Exception as exc:
        pytest.skip(f"Invalid {_RETENTION_DSN_ENV} value: {exc}")

    with engine.connect() as conn:
        try:
            row = conn.execute(text("SELECT version()")).scalar_one()
        except Exception as exc:
            engine.dispose()
            pytest.skip(f"Timescale DSN unavailable: {exc}")
        if not row or "PostgreSQL" not in str(row):
            engine.dispose()
            pytest.skip("Timescale integration tests require a reachable PostgreSQL DSN.")

    return engine


def _require_timescaledb(conn):
    installed = conn.execute(
        text("SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'")
    ).scalar()
    if not installed:
        pytest.skip("TimescaleDB extension is not installed on the test PostgreSQL.")


def _prepare_market_ohlcv_table(conn):
    conn.execute(text("DROP TABLE IF EXISTS market_ohlcv CASCADE"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
    conn.execute(text("""
            CREATE TABLE market_ohlcv (
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                candle_time TIMESTAMPTZ NOT NULL,
                open NUMERIC NOT NULL,
                high NUMERIC NOT NULL,
                low NUMERIC NOT NULL,
                close NUMERIC NOT NULL,
                volume NUMERIC NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (symbol, timeframe, candle_time, source)
            )
            """))
    conn.execute(text("""
            CREATE UNIQUE INDEX uq_market_ohlcv_symbol_timeframe_candle_time
            ON market_ohlcv (symbol, timeframe, candle_time)
            """))
    conn.execute(text("""
            CREATE INDEX idx_market_ohlcv_symbol_timeframe_time
            ON market_ohlcv (symbol, timeframe, candle_time DESC)
            """))
    conn.execute(text("""
            SELECT create_hypertable('market_ohlcv', 'candle_time', if_not_exists => TRUE)
            """))
    conn.execute(text("""
            ALTER TABLE market_ohlcv SET (
                timescaledb.compress,
                timescaledb.compress_orderby = 'candle_time DESC',
                timescaledb.compress_segmentby = 'symbol, timeframe, source'
            )
            """))
    conn.execute(text("""
            SELECT add_retention_policy('market_ohlcv', INTERVAL '2 years', if_not_exists => TRUE)
            """))
    conn.execute(text("""
            SELECT add_compression_policy('market_ohlcv', INTERVAL '30 days', if_not_exists => TRUE)
            """))


def _build_ohlcv_df(start_time: datetime, count: int, offset_seconds: int = 60) -> pd.DataFrame:
    rows = []
    for i in range(count):
        ts = start_time + timedelta(seconds=i * offset_seconds)
        rows.append(
            {
                "timestamp_utc": ts,
                "open": 100.0 + i,
                "high": 101.0 + i,
                "low": 99.0 + i,
                "close": 100.5 + i,
                "volume": 10.0 + i,
            }
        )
    return pd.DataFrame(rows)


def _repo_for_integration(monkeypatch):
    engine = _build_test_engine()
    monkeypatch.setattr(database_module, "DB_URL", os.environ[_RETENTION_DSN_ENV])
    monkeypatch.setattr(database_module, "engine", engine)
    monkeypatch.setattr(ohlcv_storage, "DB_URL", os.environ[_RETENTION_DSN_ENV])
    monkeypatch.setattr(ohlcv_storage, "engine", engine)
    return engine, ohlcv_storage.MarketOhlcvRepository()


def _run_retention_job(conn, job_name: str = "policy_retention") -> bool:
    job_id = conn.execute(
        text("""
            SELECT id
            FROM timescaledb_information.jobs
            WHERE proc_name = :job_name
              AND hypertable_name = 'market_ohlcv'
            ORDER BY id
            LIMIT 1
            """),
        {"job_name": job_name},
    ).scalar()
    if not job_id:
        return False

    try:
        conn.execute(text("SELECT run_job(:job_id)"), {"job_id": int(job_id)})
        return True
    except Exception:
        return False


def _policy_rows(conn):
    return conn.execute(text("""
            SELECT proc_name, config
            FROM timescaledb_information.jobs
            WHERE hypertable_name = 'market_ohlcv'
              AND proc_name IN ('policy_retention', 'policy_compression')
            ORDER BY proc_name
            """)).mappings().all()


def test_ohlcv_repository_insert_upsert_and_query_filters_timeframe(monkeypatch):
    engine, repo = _repo_for_integration(monkeypatch)
    with engine.begin() as conn:
        _require_timescaledb(conn)
        _prepare_market_ohlcv_table(conn)
        start = datetime.now(timezone.utc).replace(second=0, microsecond=0)

        first = _build_ohlcv_df(start, 3, 60)
        second = _build_ohlcv_df(start, 3, 60).copy()
        second.loc[1, "close"] = 555.0
        duplicate_row = second.head(1).copy()
        second = pd.concat([second, duplicate_row], ignore_index=True)

        written = repo.write_candles("BTC/USDT", "1m", "ccxt", first)
        assert written == 3
        assert len(first) == 3
        assert repo.write_candles("BTC/USDT", "1m", "ccxt", second) == 3

        # duplicate timestamp in payload should be collapsed to avoid inflated counts
        second_with_local_dup = second.copy()
        assert repo.write_candles("BTC/USDT", "1m", "ccxt", second_with_local_dup) == 3

        written_5m = repo.write_candles("BTC/USDT", "5m", "ccxt", first)
        assert written_5m == 3

        count_1m = conn.execute(text("""
                SELECT COUNT(*)
                FROM market_ohlcv
                WHERE symbol = 'BTC/USDT'
                  AND timeframe = '1m'
                """)).scalar_one()
        count_5m = conn.execute(text("""
                SELECT COUNT(*)
                FROM market_ohlcv
                WHERE symbol = 'BTC/USDT'
                  AND timeframe = '5m'
                """)).scalar_one()
        assert count_1m == 3
        assert count_5m == 3

        candles_1m = repo.read_recent_candles("BTC/USDT", "1m", 100)
        assert len(candles_1m) == 3
        assert {c["source"] for c in candles_1m} == {"ccxt"}
        assert candles_1m[-1]["close"] == 102.5
        assert any(c["close"] == 555.0 for c in candles_1m)

        assert len(repo.read_recent_candles("BTC/USDT", "5m", 100)) == 3

        assert (
            conn.execute(
                text("""
                    SELECT open
                    FROM market_ohlcv
                    WHERE symbol = 'BTC/USDT'
                      AND timeframe = '1m'
                      AND candle_time = :ts
                    """),
                {"ts": start},
            ).scalar_one()
            > 100.0
        )


def test_ohlcv_retention_policy_enforces_synthetic_rows_window(monkeypatch):
    engine, repo = _repo_for_integration(monkeypatch)
    with engine.begin() as conn:
        _require_timescaledb(conn)
        _prepare_market_ohlcv_table(conn)

        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        old_start = now - timedelta(days=820)
        recent_start = now - timedelta(days=10)

        old_rows = _build_ohlcv_df(old_start, 2, 60)
        recent_rows = _build_ohlcv_df(recent_start, 2, 60)
        assert repo.write_candles("BTC/USDT", "1h", "ccxt", old_rows) == 2
        assert repo.write_candles("BTC/USDT", "1h", "ccxt", recent_rows) == 2

        pre_count = conn.execute(text("SELECT COUNT(*) FROM market_ohlcv")).scalar_one()
        assert pre_count == 4

        if not _run_retention_job(conn):
            pytest.skip("run_job function is not available in this TimescaleDB environment.")

        cutoff = now - timedelta(days=730)
        old_count = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM market_ohlcv
                WHERE candle_time < :cutoff
                """),
            {"cutoff": cutoff},
        ).scalar_one()
        remaining = conn.execute(
            text("""
                SELECT COUNT(*)
                FROM market_ohlcv
                WHERE candle_time >= :cutoff
                """),
            {"cutoff": cutoff},
        ).scalar_one()

        assert old_count == 0
        assert remaining == 2


def test_ohlcv_timescale_policy_verification(monkeypatch):
    engine, _ = _repo_for_integration(monkeypatch)
    with engine.begin() as conn:
        _require_timescaledb(conn)
        _prepare_market_ohlcv_table(conn)

        rows = _policy_rows(conn)
        assert len(rows) == 2
        policies = {row["proc_name"]: str(row["config"]) for row in rows}
        assert "policy_retention" in policies
        assert "policy_compression" in policies
        assert "2 years" in policies["policy_retention"]
        assert "30 days" in policies["policy_compression"]

        assert conn.execute(text("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = 'market_ohlcv'
                          AND n.nspname = 'public'
                          AND EXISTS (
                                SELECT 1
                                FROM unnest(c.reloptions) AS opt(v)
                                WHERE lower(v::text) LIKE 'timescaledb.compress=%'
                          )
                    )
                    """)).scalar_one()


def test_ohlcv_read_latency_under_500ms_with_limit_filter(monkeypatch):
    if not os.getenv(_PERF_ENFORCE_ENV):
        pytest.skip("Set MARKET_OHLCV_PERF_TESTS=1 to run performance regression check.")

    engine, repo = _repo_for_integration(monkeypatch)
    with engine.begin() as conn:
        _require_timescaledb(conn)
        _prepare_market_ohlcv_table(conn)
        end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        base = end - timedelta(minutes=20_000)

        large = _build_ohlcv_df(base, count=20_000, offset_seconds=60)
        assert repo.write_candles("BTC/USDT", "1m", "ccxt", large) == 20_000

        since = end - timedelta(days=180)
        until = end
        timings = []
        import time as time_module

        for _ in range(25):
            start = time_module.perf_counter()
            rows = conn.execute(
                text("""
                    SELECT candle_time, open, high, low, close, volume, source
                    FROM market_ohlcv
                    WHERE symbol = :symbol
                      AND timeframe = :timeframe
                      AND candle_time >= :since
                      AND candle_time <= :until
                    ORDER BY candle_time DESC
                    LIMIT 400
                    """),
                {
                    "symbol": "BTC/USDT",
                    "timeframe": "1m",
                    "since": since,
                    "until": until,
                },
            ).all()
            timings.append(time_module.perf_counter() - start)
            assert len(rows) >= 1

    p95 = sorted(timings)[int(len(timings) * 0.95) - 1]
    assert p95 < 0.5
