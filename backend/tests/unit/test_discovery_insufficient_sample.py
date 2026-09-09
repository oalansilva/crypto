"""Listing gate and 4-term reconcile for discovery (card #876)."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.discovery_service import MIN_ELIGIBLE_TRADES
from app.tasks.discovery_tasks import (
    DISCOVERY_SPLIT_TRAIN_RATIO,
    evaluate_listing_sample,
    reconcile_sweep,
    run_combination,
)


def _ensure_schema(engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "ALTER TABLE discovery_sweeps ADD COLUMN IF NOT EXISTS "
            "insufficient_sample INTEGER NOT NULL DEFAULT 0"
        )
        connection.exec_driver_sql(
            "ALTER TABLE discovery_results ALTER COLUMN eligibility TYPE VARCHAR(32)"
        )


def _ohlcv_frame(n: int, freq: str = "D") -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame(
        {
            "open": 1.0,
            "high": 1.0,
            "low": 1.0,
            "close": 1.0,
            "volume": 1.0,
        },
        index=idx,
    )


class _FakeProvider:
    def __init__(self, df: pd.DataFrame | None):
        self.df = df
        self.calls = 0

    def fetch_ohlcv(self, **_kwargs):
        self.calls += 1
        return self.df


def _patch_provider(monkeypatch, df: pd.DataFrame | None) -> _FakeProvider:
    provider = _FakeProvider(df)
    monkeypatch.setattr(
        "app.services.market_data_providers.get_market_data_provider",
        lambda *_a, **_k: provider,
    )
    monkeypatch.setattr(
        "app.services.market_data_providers.resolve_data_source_for_symbol",
        lambda *_a, **_k: "ccxt",
    )
    monkeypatch.setattr(
        "app.services.market_data_providers.validate_data_source_timeframe",
        lambda *_a, **_k: "ccxt",
    )
    return provider


def test_evaluate_listing_27_daily_bars_is_insufficient(monkeypatch):
    _patch_provider(monkeypatch, _ohlcv_frame(27))
    insufficient, listing_len, train_len = evaluate_listing_sample(
        symbol="BLZ/USDT",
        timeframe="1d",
        start_date=None,
        end_date=None,
    )
    assert listing_len == 27
    assert train_len == int(27 * DISCOVERY_SPLIT_TRAIN_RATIO)
    assert train_len < MIN_ELIGIBLE_TRADES
    assert insufficient is True


def test_evaluate_listing_empty_is_insufficient(monkeypatch):
    _patch_provider(monkeypatch, pd.DataFrame())
    insufficient, listing_len, train_len = evaluate_listing_sample(
        symbol="BLZ/USDT",
        timeframe="1d",
        start_date="2017-01-01",
        end_date="2026-09-08",
    )
    assert insufficient is True
    assert listing_len == 0
    assert train_len == 0


def test_evaluate_listing_enough_bars_is_sufficient(monkeypatch):
    _patch_provider(monkeypatch, _ohlcv_frame(50))
    insufficient, listing_len, train_len = evaluate_listing_sample(
        symbol="BTC/USDT",
        timeframe="1d",
        start_date="2024-01-01",
        end_date="2024-12-31",
    )
    assert listing_len == 50
    assert train_len >= MIN_ELIGIBLE_TRADES
    assert insufficient is False


class _BoomOptimizer:
    def __init__(self, *_a, **_k):
        raise AssertionError("ComboOptimizer must not be constructed on listing cut")

    def generate_stages(self, *_a, **_k):
        raise AssertionError("generate_stages must not run on listing cut")

    def run_optimization(self, *_a, **_k):
        raise AssertionError("run_optimization must not run on listing cut")


def _patch_metadata(monkeypatch) -> None:
    from app.services.combo_service import ComboService

    monkeypatch.setattr(
        ComboService,
        "get_template_metadata",
        lambda _self, _name: {
            "name": "MACD_Cross",
            "direction": "long",
            "indicators": [],
            "optimization_schema": {},
        },
    )


def _seed_running(db, *, sweep_id: str, total: int = 1):
    from app.models_discovery import DiscoveryCombination, DiscoverySweep

    sweep = DiscoverySweep(
        id=sweep_id,
        actor="test",
        state="running",
        idempotency_key=f"key-{sweep_id}",
        payload_hash="a" * 64,
        snapshot_token=f"tok-{sweep_id}",
        snapshot_hash="b" * 64,
        snapshot={"period_type": "all"},
        total=total,
    )
    combo = DiscoveryCombination(
        sweep_id=sweep.id,
        template_id="MACD_Cross",
        symbol="BLZ/USDT",
        timeframe="1d",
        direction="long",
        state="running",
    )
    db.add(sweep)
    db.add(combo)
    db.commit()
    return sweep, combo


class TestRunCombinationListingGate:
    def test_short_daily_listing_skips_grid(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        _ensure_schema(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        _sweep, combo = _seed_running(db, sweep_id="sw-876-short")
        _patch_provider(monkeypatch, _ohlcv_frame(27))
        _patch_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", _BoomOptimizer)

        started = time.monotonic()
        try:
            run_combination(db, combo, owner="worker-876")
            elapsed = time.monotonic() - started
            db.refresh(combo)
            result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
            assert elapsed < 5
            assert combo.state == "insufficient_sample"
            assert result.eligibility == "insufficient_sample"
            assert result.calmar_ratio is None
            assert result.max_drawdown is None
            assert result.trades_count is None
            assert result.coverage is None
        finally:
            db.close()

    def test_sufficient_listing_still_runs_optimizer(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        _ensure_schema(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        _sweep, combo = _seed_running(db, sweep_id="sw-876-ok")
        _patch_provider(monkeypatch, _ohlcv_frame(50))
        _patch_metadata(monkeypatch)
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)
        constructed = {"n": 0}

        class FakeOptimizer:
            def __init__(self):
                constructed["n"] += 1

            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 1.2,
                        "profit_factor": 1.5,
                        "max_drawdown": 0.15,
                        "win_rate": 0.55,
                        "cagr": 0.42,
                        "calmar_ratio": 2.8,
                        "benchmark": {"cagr": 0.18},
                    },
                    "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 40,
                    "candles": [
                        {"timestamp_utc": start.isoformat(), "close": 1.0},
                        {"timestamp_utc": end.isoformat(), "close": 1.0},
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                }

        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)
        try:
            run_combination(db, combo, owner="worker-876")
            db.refresh(combo)
            result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
            assert constructed["n"] == 1
            assert combo.state == "succeeded"
            assert result.eligibility == "eligible"
        finally:
            db.close()


class TestReconcileFourTerm:
    def test_insufficient_only_completes(
        self, postgres_isolation, unit_database_url
    ):
        from app.models_discovery import DiscoveryCombination, DiscoverySweep

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        _ensure_schema(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        sweep = DiscoverySweep(
            id="sw-876-ins-only",
            actor="test",
            state="running",
            idempotency_key="k-ins",
            payload_hash="a" * 64,
            snapshot_token="tok",
            snapshot_hash="b" * 64,
            snapshot={},
            total=2,
        )
        db.add(sweep)
        for i in range(2):
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep.id,
                    template_id="t1",
                    symbol=f"S{i}/USDT",
                    timeframe="1d",
                    direction="long",
                    state="insufficient_sample",
                )
            )
        db.commit()
        summary = reconcile_sweep(sweep.id, db)
        assert summary["state"] == "completed"
        assert summary["insufficient_sample"] == 2
        assert summary["succeeded"] == 0
        assert summary["failed"] == 0
        assert summary["processed"] == 2 == summary["total"]
        assert summary.get("terminal_reason") in (None, "")
        db.refresh(sweep)
        assert sweep.terminal_reason is None
        db.close()

    def test_skipped_only_remains_operational_failure(
        self, postgres_isolation, unit_database_url
    ):
        from app.models_discovery import DiscoveryCombination, DiscoverySweep

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        _ensure_schema(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        sweep = DiscoverySweep(
            id="sw-876-skip-only",
            actor="test",
            state="running",
            idempotency_key="k-skip",
            payload_hash="a" * 64,
            snapshot_token="tok",
            snapshot_hash="b" * 64,
            snapshot={},
            total=2,
        )
        db.add(sweep)
        for i in range(2):
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep.id,
                    template_id="t1",
                    symbol=f"S{i}/USDT",
                    timeframe="1d",
                    direction="long",
                    state="skipped",
                )
            )
        db.commit()
        summary = reconcile_sweep(sweep.id, db)
        assert summary["state"] == "failed"
        assert summary["skipped"] == 2
        assert summary["insufficient_sample"] == 0
        db.refresh(sweep)
        assert sweep.terminal_reason == "operational_failure"
        db.close()

    def test_four_term_processed_formula(
        self, postgres_isolation, unit_database_url
    ):
        from app.models_discovery import DiscoveryCombination, DiscoverySweep

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        _ensure_schema(engine)
        Session = sessionmaker(bind=engine)
        db = Session()
        sweep = DiscoverySweep(
            id="sw-876-four",
            actor="test",
            state="running",
            idempotency_key="k-four",
            payload_hash="a" * 64,
            snapshot_token="tok",
            snapshot_hash="b" * 64,
            snapshot={},
            total=18,
        )
        db.add(sweep)
        states = (
            ["succeeded"] * 12
            + ["failed"] * 1
            + ["skipped"] * 1
            + ["insufficient_sample"] * 4
        )
        for i, state in enumerate(states):
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep.id,
                    template_id="t1",
                    symbol=f"S{i}/USDT",
                    timeframe="1d",
                    direction="long",
                    state=state,
                )
            )
        db.commit()
        summary = reconcile_sweep(sweep.id, db)
        assert summary["processed"] == 12 + 1 + 1 + 4
        assert summary["processed"] == summary["total"]
        assert summary["state"] == "partial_failure"
        db.close()
