"""Frozen candles survive provider changes, and clean only owned files."""

import json
from pathlib import Path

import pandas as pd
import pytest

from app.services import discovery_inputs as inputs
from app.services.discovery_resources import (
    OperationalFailure,
    cleanup_orphan_spools,
    mark_spool_owner,
)


def test_frozen_snapshot_retry_identity_corruption_and_cleanup(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    frame = pd.DataFrame(
        {
            "open": [1.0, 2.0],
            "high": [2.0, 3.0],
            "low": [0.0, 1.0],
            "close": [1.0, 2.0],
            "volume": [1.0, 1.0],
        },
        index=pd.date_range("2025-10-06", periods=2, tz="UTC"),
    )
    frame.index.freq = None  # Real timestamp-indexed market windows have no inferred frequency.
    monkeypatch.setattr(
        "app.services.market_data_providers.CcxtMarketDataProvider.fetch_ohlcv",
        lambda *_args, **_kwargs: frame,
    )
    monkeypatch.setattr(
        "src.data.incremental_loader.IncrementalLoader.fetch_intraday_data",
        lambda *_args, **_kwargs: frame,
    )
    manifest = inputs.prepare(
        dict(symbol="BTC/USDT", timeframe="15m", start_date="2025-10-06", end_date="2026-10-06")
    )

    def unexpected(*_args, **_kwargs):
        raise AssertionError("Retry must not ask a provider again")

    monkeypatch.setattr(
        "app.services.market_data_providers.CcxtMarketDataProvider.fetch_ohlcv", unexpected
    )
    assert inputs.prepare({"candle_manifest": manifest}) == manifest
    monkeypatch.setenv("DISCOVERY_FROZEN_INPUT_DIR", manifest["directory"])
    pd.testing.assert_frame_equal(inputs.FrozenProvider().fetch_ohlcv(), frame, check_exact=True)
    path = Path(manifest["directory"]) / "candles.parquet"
    path.write_bytes(b"corrupt")
    with pytest.raises(OperationalFailure, match="frozen_input_corrupt"):
        inputs.prepare({"candle_manifest": manifest})
    inputs.discard(manifest)
    assert not list(tmp_path.iterdir())


def test_orphans_are_removed_only_after_owner_identity_is_proven_gone(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    current = tmp_path / "attempt-live"
    current.mkdir()
    mark_spool_owner(current)
    dead = tmp_path / "attempt-dead"
    dead.mkdir()
    (dead / "owner.json").write_text(json.dumps({"pid": 999999999, "start": "missing"}))
    (dead / "results.sqlite").write_bytes(b"private")
    unknown = tmp_path / "attempt-unknown"
    unknown.mkdir()
    cleanup_orphan_spools()
    assert current.exists() and unknown.exists() and not dead.exists()
