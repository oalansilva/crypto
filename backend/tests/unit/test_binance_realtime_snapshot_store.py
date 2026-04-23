from __future__ import annotations

import time
from types import SimpleNamespace

import app.services.binance_realtime_snapshot_store as snapshot_store


def test_snapshot_store_round_trip_and_freshness(monkeypatch, tmp_path):
    snapshot_path = tmp_path / "runtime" / "snapshot.json"
    monkeypatch.setattr(
        snapshot_store,
        "get_settings",
        lambda: SimpleNamespace(
            binance_realtime_snapshot_path=str(snapshot_path),
            binance_realtime_snapshot_max_age_seconds=15.0,
        ),
    )

    payload = {"running": True, "heartbeat_ts": 100.0, "now_ts": 110.0, "prices": []}
    assert snapshot_store.get_snapshot_path() == snapshot_path
    snapshot_store.write_snapshot(payload)
    assert snapshot_store.read_snapshot() == payload
    assert snapshot_store.snapshot_is_fresh(payload) is True
    assert snapshot_store.snapshot_is_fresh({"heartbeat_ts": "bad"}) is False


def test_snapshot_store_env_default_and_invalid_payloads(monkeypatch, tmp_path):
    env_path = tmp_path / "env-snapshot.json"
    monkeypatch.setenv("BINANCE_REALTIME_SNAPSHOT_PATH", str(env_path))
    monkeypatch.setattr(snapshot_store, "get_settings", lambda: SimpleNamespace())

    assert snapshot_store.get_snapshot_path() == env_path
    assert snapshot_store.read_snapshot() is None

    env_path.write_text("[1,2,3]", encoding="utf-8")
    assert snapshot_store.read_snapshot() is None

    env_path.write_text("{bad", encoding="utf-8")
    assert snapshot_store.read_snapshot() is None

    monkeypatch.delenv("BINANCE_REALTIME_SNAPSHOT_PATH", raising=False)
    monkeypatch.setattr(
        snapshot_store,
        "get_settings",
        lambda: SimpleNamespace(
            binance_realtime_snapshot_path=None,
            binance_realtime_snapshot_max_age_seconds=2.0,
        ),
    )
    assert snapshot_store.get_snapshot_path().name == "binance_realtime_snapshot.json"
    assert snapshot_store.snapshot_is_fresh({"heartbeat_ts": 100.0, "now_ts": 103.5}) is False
    monkeypatch.setattr(time, "time", lambda: 101.0)
    assert snapshot_store.snapshot_is_fresh({"heartbeat_ts": 100.0}) is True
