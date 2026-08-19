"""Unit tests for discovery leaderboard ranking metrics (card #599)."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.combo_optimizer import _enrich_ranking_metrics


def _sample_trades() -> list[dict]:
    return [
        {
            "entry_time": "2024-01-10T00:00:00+00:00",
            "profit": 0.10,
        },
        {
            "entry_time": "2024-02-10T00:00:00+00:00",
            "profit": 0.05,
        },
    ]


def _sample_close() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=120, freq="D", tz="UTC")
    return pd.Series([100.0 + i * 0.5 for i in range(len(idx))], index=idx)


class TestEnrichRankingMetrics:
    def test_discovery_path_with_trades_populates_finite_metrics(self):
        metrics: dict = {"max_drawdown": 0.12}

        _enrich_ranking_metrics(
            _sample_trades(),
            _sample_close(),
            metrics,
            legacy_zero_trade_ranking=False,
        )

        assert "cagr" in metrics
        assert "calmar_ratio" in metrics
        assert "benchmark" in metrics
        assert math.isfinite(metrics["cagr"])
        assert math.isfinite(metrics["calmar_ratio"])
        assert math.isfinite(float(metrics["benchmark"]["cagr"]))

    def test_discovery_path_zero_trades_omits_ranking_keys(self):
        metrics: dict = {"max_drawdown": 0.0, "sharpe_ratio": 0.0}

        _enrich_ranking_metrics(
            [],
            _sample_close(),
            metrics,
            legacy_zero_trade_ranking=False,
        )

        assert "cagr" not in metrics
        assert "calmar_ratio" not in metrics
        assert "benchmark" not in metrics

    def test_legacy_path_zero_trades_preserves_zero_cagr(self):
        metrics: dict = {"max_drawdown": 0.0}

        _enrich_ranking_metrics(
            [],
            _sample_close(),
            metrics,
            legacy_zero_trade_ranking=True,
        )

        assert metrics["cagr"] == 0.0
        assert "benchmark" in metrics
        assert metrics["calmar_ratio"] == 0.0

    def test_discovery_path_never_sets_explicit_none(self):
        metrics: dict = {"max_drawdown": 0.12}

        _enrich_ranking_metrics(
            _sample_trades(),
            _sample_close(),
            metrics,
            legacy_zero_trade_ranking=False,
        )

        for key in ("cagr", "calmar_ratio"):
            if key in metrics:
                assert metrics[key] is not None
        if "benchmark" in metrics:
            assert metrics["benchmark"].get("cagr") is not None


class TestDiscoveryRankingPersistence:
    def test_run_combination_persists_ranking_columns(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryCombination, DiscoveryResult, DiscoverySweep
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()

        sweep = DiscoverySweep(
            id="sw-ranking-599",
            actor="test",
            state="running",
            idempotency_key="key-599",
            payload_hash="a" * 64,
            snapshot_token="tok-599",
            snapshot_hash="b" * 64,
            snapshot={"period_type": "2y"},
            total=1,
        )
        combo = DiscoveryCombination(
            sweep_id=sweep.id,
            template_id="MACD_Cross",
            symbol="ETH/USDT",
            timeframe="1d",
            direction="long",
            state="running",
        )
        db.add(sweep)
        db.add(combo)
        db.commit()

        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, tzinfo=timezone.utc)

        captured: dict = {}

        class FakeOptimizer:
            def run_optimization(self, **kwargs):
                captured.update(kwargs)
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
                    "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 22,
                    "candles": [
                        {
                            "timestamp_utc": start.isoformat(),
                            "open": 1.0,
                            "high": 1.0,
                            "low": 1.0,
                            "close": 1.0,
                            "volume": 1.0,
                        },
                        {
                            "timestamp_utc": end.isoformat(),
                            "open": 1.0,
                            "high": 1.0,
                            "low": 1.0,
                            "close": 1.0,
                            "volume": 1.0,
                        },
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_metrics": {"total_trades": 12, "sharpe_ratio": 0.4, "cagr": 0.11},
                    "oos_verdict": {"status": "GO", "reasons": ["ok"], "split_train_ratio": 0.7},
                }

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
        monkeypatch.setattr(
            "app.services.combo_optimizer.ComboOptimizer",
            FakeOptimizer,
        )

        run_combination(db, combo, owner="worker-599")
        db.refresh(combo)

        assert combo.state == "succeeded"
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert captured.get("deep_backtest") is True
        assert captured.get("split_train_ratio") == pytest.approx(0.7)
        assert result.cagr == pytest.approx(0.42)
        assert result.calmar_ratio == pytest.approx(2.8)
        assert result.benchmark_cagr == pytest.approx(0.18)
        assert result.delta_cagr_vs_bh == pytest.approx((0.42 - 0.18) * 100)
        assert result.metrics["split_train_ratio"] == pytest.approx(0.7)
        assert result.metrics["split_applied"] is True
        assert result.metrics["oos_metrics"]["total_trades"] == 12
        assert result.metrics["oos_verdict"]["status"] == "GO"
        db.close()


def _patch_combo_metadata(monkeypatch) -> None:
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


def _seed_running_combination(db, *, sweep_id: str, snapshot: dict | None = None):
    from app.models_discovery import DiscoveryCombination, DiscoverySweep

    sweep = DiscoverySweep(
        id=sweep_id,
        actor="test",
        state="running",
        idempotency_key=f"key-{sweep_id}",
        payload_hash="a" * 64,
        snapshot_token=f"tok-{sweep_id}",
        snapshot_hash="b" * 64,
        snapshot=snapshot or {"period_type": "2y"},
        total=1,
    )
    combo = DiscoveryCombination(
        sweep_id=sweep.id,
        template_id="MACD_Cross",
        symbol="ETH/USDT",
        timeframe="1d",
        direction="long",
        state="running",
    )
    db.add(sweep)
    db.add(combo)
    db.commit()
    return combo


class TestDiscoveryWalkForwardPersistence:
    def test_zero_trades_with_zero_cagr_persists_null_ranking(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()
        combo = _seed_running_combination(db, sweep_id="sw-wf-zero")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 12, 31, tzinfo=timezone.utc)

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 0.0,
                        "profit_factor": 0.0,
                        "max_drawdown": 0.0,
                        "win_rate": 0.0,
                        "cagr": 0.0,
                        "calmar_ratio": 0.0,
                        "benchmark": {"cagr": 0.12},
                    },
                    "trades": [],
                    "candles": [
                        {
                            "timestamp_utc": start.isoformat(),
                            "close": 100.0,
                        },
                        {
                            "timestamp_utc": end.isoformat(),
                            "close": 140.0,
                        },
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_metrics": {"total_trades": 0, "sharpe_ratio": 0.2},
                    "oos_verdict": {"status": "NO-GO", "reasons": ["Poucos trades"]},
                }

        _patch_combo_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)

        run_combination(db, combo, owner="worker-605")
        db.refresh(combo)
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert result.cagr is None
        assert result.calmar_ratio is None
        assert result.benchmark_cagr is None
        assert result.delta_cagr_vs_bh is None
        assert "cagr" not in result.metrics
        assert result.metrics["split_train_ratio"] == pytest.approx(0.7)
        assert result.metrics["oos_verdict"]["status"] == "NO-GO"
        assert result.eligibility == "low_sample"
        db.close()

    def test_holdout_error_enriches_in_sample_ranking(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()
        combo = _seed_running_combination(db, sweep_id="sw-wf-error")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        candles = []
        close = 100.0
        for i in range(120):
            ts = datetime(2024, 1, 1, tzinfo=timezone.utc) + pd.Timedelta(days=i)
            candles.append(
                {
                    "timestamp_utc": ts.isoformat(),
                    "open": close,
                    "high": close,
                    "low": close,
                    "close": close + 0.4,
                    "volume": 1.0,
                }
            )
            close += 0.4

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 1.1,
                        "profit_factor": 1.4,
                        "max_drawdown": 0.12,
                        "win_rate": 0.5,
                    },
                    "trades": [
                        {"entry_time": start.isoformat(), "profit": 0.10},
                        {
                            "entry_time": datetime(2024, 2, 10, tzinfo=timezone.utc).isoformat(),
                            "profit": 0.05,
                        },
                    ],
                    "candles": candles,
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_metrics": None,
                    "oos_verdict": {"status": "ERROR", "reasons": ["holdout falhou"]},
                }

        _patch_combo_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)

        run_combination(db, combo, owner="worker-605")
        db.refresh(combo)
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert result.cagr is not None and math.isfinite(result.cagr)
        assert result.calmar_ratio is not None and math.isfinite(result.calmar_ratio)
        assert result.benchmark_cagr is not None and math.isfinite(result.benchmark_cagr)
        assert result.metrics["oos_verdict"]["status"] == "ERROR"
        assert result.metrics["split_applied"] is True
        db.close()

    def test_coverage_uses_in_sample_candle_window_not_sweep_snapshot(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()
        combo = _seed_running_combination(
            db,
            sweep_id="sw-wf-window",
            snapshot={
                "period_type": "2y",
                "start_date": "2024-01-01",
                "end_date": "2026-01-01",
            },
        )
        is_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        is_end = datetime(2024, 7, 1, tzinfo=timezone.utc)

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 1.0,
                        "profit_factor": 1.2,
                        "max_drawdown": 0.1,
                        "win_rate": 0.5,
                        "cagr": 0.2,
                        "calmar_ratio": 2.0,
                        "benchmark": {"cagr": 0.1},
                    },
                    "trades": [{"entry_time": is_start.isoformat(), "profit": 0.1}] * 40,
                    "candles": [
                        {"timestamp_utc": is_start.isoformat(), "close": 100.0},
                        {"timestamp_utc": is_end.isoformat(), "close": 110.0},
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_verdict": {"status": "NO-GO", "reasons": ["Sharpe baixo"]},
                }

        _patch_combo_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)

        run_combination(db, combo, owner="worker-605")
        db.refresh(combo)
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert result.start_at.replace(tzinfo=None) == is_start.replace(tzinfo=None)
        assert result.end_at.replace(tzinfo=None) == is_end.replace(tzinfo=None)
        two_year_days = (
            datetime(2026, 1, 1, tzinfo=timezone.utc) - datetime(2024, 1, 1, tzinfo=timezone.utc)
        ).days
        assert result.expected_candles is not None
        assert result.expected_candles < two_year_days
        assert result.expected_candles == (is_end - is_start).days
        assert result.observed_valid_candles == 2
        assert result.coverage == pytest.approx(2 / result.expected_candles)
        assert result.eligibility == "low_sample"
        assert result.metrics["oos_verdict"]["status"] == "NO-GO"
        db.close()

    def test_nogo_holdout_does_not_override_discovery_eligibility(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()
        combo = _seed_running_combination(db, sweep_id="sw-wf-nogo")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 1.0,
                        "profit_factor": 1.2,
                        "max_drawdown": 0.1,
                        "win_rate": 0.5,
                        "cagr": 0.2,
                        "calmar_ratio": 2.0,
                        "benchmark": {"cagr": 0.1},
                    },
                    "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 40,
                    "candles": [
                        {"timestamp_utc": start.isoformat(), "close": 100.0},
                        {"timestamp_utc": end.isoformat(), "close": 101.0},
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_verdict": {"status": "NO-GO", "reasons": ["Sharpe baixo"]},
                }

        _patch_combo_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)

        run_combination(db, combo, owner="worker-605")
        db.refresh(combo)
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert result.eligibility == "eligible"
        assert result.metrics["oos_verdict"]["status"] == "NO-GO"
        db.close()

    def test_nonfinite_calmar_is_omitted_from_json_metrics(
        self, postgres_isolation, unit_database_url, monkeypatch
    ):
        from app.models_discovery import DiscoveryResult
        from app.tasks.discovery_tasks import run_combination

        engine = create_engine(unit_database_url)
        Base.metadata.create_all(bind=engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DELETE FROM discovery_results")
            connection.exec_driver_sql("DELETE FROM discovery_combinations")
            connection.exec_driver_sql("DELETE FROM discovery_sweeps")

        Session = sessionmaker(bind=engine)
        db = Session()
        combo = _seed_running_combination(db, sweep_id="sw-wf-inf")
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)

        class FakeOptimizer:
            def run_optimization(self, **_kwargs):
                return {
                    "best_metrics": {
                        "sharpe_ratio": 1.0,
                        "profit_factor": 1.2,
                        "max_drawdown": 0.0,
                        "win_rate": 0.5,
                        "cagr": 0.2,
                        "calmar_ratio": float("inf"),
                        "benchmark": {"cagr": 0.1},
                    },
                    "trades": [{"entry_time": start.isoformat(), "profit": 0.1}] * 40,
                    "candles": [
                        {"timestamp_utc": start.isoformat(), "close": 100.0},
                        {"timestamp_utc": end.isoformat(), "close": 101.0},
                    ],
                    "best_parameters": {"direction": "long"},
                    "data_source": "ccxt",
                    "oos_verdict": {"status": "GO", "reasons": ["ok"]},
                }

        _patch_combo_metadata(monkeypatch)
        monkeypatch.setattr("app.services.combo_optimizer.ComboOptimizer", FakeOptimizer)

        run_combination(db, combo, owner="worker-605")
        db.refresh(combo)
        result = db.query(DiscoveryResult).filter(DiscoveryResult.id == combo.result_id).one()
        assert result.cagr == pytest.approx(0.2)
        assert result.calmar_ratio is None
        assert "calmar_ratio" not in result.metrics
        db.close()
