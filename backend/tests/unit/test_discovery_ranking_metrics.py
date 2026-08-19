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

        class FakeOptimizer:
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
        assert result.cagr == pytest.approx(0.42)
        assert result.calmar_ratio == pytest.approx(2.8)
        assert result.benchmark_cagr == pytest.approx(0.18)
        assert result.delta_cagr_vs_bh == pytest.approx((0.42 - 0.18) * 100)
        db.close()
