from __future__ import annotations

import fcntl
import json

from app.services import runtime_status


def test_runtime_status_defaults_are_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(tmp_path / "writer.lock"))
    state_path = tmp_path / "writer.json"
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(state_path))
    monkeypatch.setenv("DATABASE_URL", "postgresql://secret-user:secret-pass@localhost/db")
    monkeypatch.delenv("MARKET_OHLCV_INGESTION_ENABLED", raising=False)
    monkeypatch.delenv("BACKFILL_SCHEDULER_ENABLED", raising=False)
    monkeypatch.delenv("BINANCE_REALTIME_ENABLED", raising=False)
    monkeypatch.delenv("CRYPTO_RUNTIME_WORKER_ENABLED", raising=False)
    monkeypatch.delenv("CRYPTO_CELERY_WORKER_ENABLED", raising=False)
    monkeypatch.delenv("BINANCE_REALTIME_WORKER_ENABLED", raising=False)

    payload = runtime_status.build_runtime_status_payload(
        market_ohlcv_enabled=True,
        market_ohlcv_metrics={"ingest": {"rows_received": 3}},
    )

    assert payload["runtime"]["canonical_candles_mode"] is True
    assert payload["runtime"]["direct_fetch_fallback"] is False
    assert payload["runtime"]["backend_ohlcv_ingestion_enabled"] is False
    assert payload["runtime"]["backfill_scheduler_enabled"] is False
    assert payload["runtime"]["binance_realtime_connector_enabled"] is False
    assert payload["workers"]["runtime_worker"]["enabled"] is False
    assert payload["workers"]["celery_batch"]["enabled"] is False
    assert payload["workers"]["binance_realtime_worker"]["enabled"] is False
    assert payload["candle_writer"]["lock"]["lock_held"] is False
    assert payload["candle_writer"]["lock"]["exists"] is False
    assert not (tmp_path / "writer.lock").exists()
    assert "secret-pass" not in json.dumps(payload)


def test_runtime_status_reports_runtime_worker_only_with_routine(monkeypatch, tmp_path):
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(tmp_path / "writer.lock"))
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(tmp_path / "writer.json"))
    monkeypatch.setenv("CRYPTO_RUNTIME_WORKER_ENABLED", "1")
    monkeypatch.setenv("RUN_SIGNAL_MONITOR", "0")
    monkeypatch.setenv("RUN_SIGNAL_FEED_SNAPSHOT_WORKER", "1")
    monkeypatch.setenv("RUN_FAVORITE_BACKTEST_REFRESH", "0")

    payload = runtime_status.build_runtime_status_payload(
        market_ohlcv_enabled=False,
        market_ohlcv_metrics={},
    )

    assert payload["workers"]["runtime_worker"]["enabled"] is True
    assert payload["workers"]["runtime_worker"]["routines"]["signal_feed_snapshot"] is True


def test_runtime_status_detects_held_writer_lock(monkeypatch, tmp_path):
    lock_path = tmp_path / "writer.lock"
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_LOCK_FILE", str(lock_path))

    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock = runtime_status.inspect_candle_writer_lock()

    assert lock["exists"] is True
    assert lock["lock_held"] is True


def test_runtime_status_sanitizes_writer_state(monkeypatch, tmp_path):
    state_path = tmp_path / "writer-state.json"
    state_path.write_text(
        json.dumps(
            {
                "status": "failed",
                "pid": 123,
                "started_at": "2026-05-22T00:00:00+00:00",
                "finished_at": "2026-05-22T00:01:00+00:00",
                "runs": 0,
                "duration_seconds": 60.0,
                "lock_path": "/tmp/crypto-candle-writer.lock",
                "error": "password=super-secret token=abc123 failure",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("CRYPTO_CANDLES_WRITER_STATE_FILE", str(state_path))

    state = runtime_status.read_candle_writer_state()

    assert state is not None
    assert state["status"] == "failed"
    assert state["pid"] == 123
    assert "lock_path" not in state
    assert "super-secret" not in state["error"]
    assert "abc123" not in state["error"]
