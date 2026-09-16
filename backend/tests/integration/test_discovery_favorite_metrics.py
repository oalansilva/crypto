"""GET flatten and persist overlay for discovery-promoted favorites (card #897)."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import favorites

SNAPSHOT_193 = {
    "sharpe_ratio": 0.31,
    "win_rate": 0.467,
    "total_return": 169.51,
    "total_return_pct": 16951,
    "max_drawdown": 0.165,
    "total_trades": 30,
    "profit_factor": 1.42,
}


@pytest.fixture(autouse=True)
def _disable_live_favorite_candle_repository(monkeypatch):
    class DisabledRepository:
        enabled = False

    monkeypatch.setattr(favorites, "_FAVORITE_OHLCV_REPO", DisabledRepository())


def _session_factory(tmp_path: Path):
    del tmp_path
    engine = create_engine(os.environ["DATABASE_URL"])
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE favorite_strategies ADD COLUMN IF NOT EXISTS notify_telegram BOOLEAN NOT NULL DEFAULT TRUE"
            )
        )
        connection.execute(
            text(
                "DELETE FROM favorite_strategies WHERE user_id IN ('user-a', 'user-b', 'admin-user')"
            )
        )
    return TestingSessionLocal


def _discovery_metrics(**overrides):
    payload = {
        "origin_type": "discovery_sweep",
        "sweep_id": "sw-193",
        "result_id": "RS-B109ED2C80",
        "strategy_identity_key": "id-193",
        "evidence_fingerprint": "fp-193",
        "metrics_snapshot": SNAPSHOT_193,
        "promoted_at": "2026-09-11T00:00:00Z",
    }
    payload.update(overrides)
    return payload


def _create(db, *, name: str, symbol: str, metrics: dict, **extra):
    payload = {
        "name": name,
        "symbol": symbol,
        "timeframe": "1d",
        "strategy_name": "multi_ma_crossover",
        "parameters": {"direction": "long"},
        "metrics": metrics,
        "period_type": "all",
        **extra,
    }
    return favorites.create_favorite(
        favorites.FavoriteStrategyCreate(**payload),
        current_user_id="user-a",
        db=db,
    )


def test_get_already_promoted_193_fills_grid_keys_from_snapshot(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = _create(
            db,
            name="ALPHA Descoberta",
            symbol="ALPHA/USDT",
            metrics=_discovery_metrics(),
            tier=3,
            start_date="2020-10-10",
            end_date="2024-02-01",
        )
        listed = favorites.list_favorites(current_user_id="user-a", db=db)

    row = next(item for item in listed if item.id == created.id)
    metrics = row.metrics
    assert metrics["sharpe_ratio"] == pytest.approx(0.31)
    assert metrics["total_trades"] == 30
    assert metrics["win_rate"] == pytest.approx(0.467)
    assert metrics["total_return_pct"] == 16951
    assert metrics["max_drawdown"] == pytest.approx(0.165)
    assert metrics["profit_factor"] == pytest.approx(1.42)
    assert metrics["origin_type"] == "discovery_sweep"
    assert metrics["result_id"] == "RS-B109ED2C80"
    assert metrics["metrics_snapshot"]["total_trades"] == 30


def test_combo_saved_get_contract_unchanged(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = _create(
            db,
            name="Combo BTC",
            symbol="BTC/USDT",
            metrics={
                "sharpe_ratio": 0.5,
                "win_rate": 0.583,
                "total_return": 199.27,
                "total_return_pct": 19927,
                "max_drawdown": 0.122,
                "total_trades": 72,
            },
        )
        listed = favorites.list_favorites(current_user_id="user-a", db=db)

    row = next(item for item in listed if item.id == created.id)
    assert "origin_type" not in (row.metrics or {})
    assert row.metrics["sharpe_ratio"] == pytest.approx(0.5)
    assert row.metrics["total_trades"] == 72
    assert row.metrics["total_return_pct"] == 19927
    assert "metrics_snapshot" not in (row.metrics or {})


def test_persist_regenerated_trades_does_not_overwrite_snapshot_keys(tmp_path: Path, monkeypatch):
    SessionLocal = _session_factory(tmp_path)
    monkeypatch.setattr(favorites, "can_view_strategy_secrets", lambda *_args, **_kwargs: True)

    async def fake_run_favorite_optimization(_favorite):
        return {
            "best_metrics": {
                "total_trades": 12,
                "win_rate": 0.333,
                "total_return": -0.1392,
                "total_return_pct": -13.92,
                "profit_factor": 0.8,
            },
            "trades": [{"entry_time": "2026-01-01T00:00:00Z", "profit": -0.01}] * 12,
            "candles": [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 100}],
            "indicator_data": {"sma_medium": [99]},
            "execution_mode": "fast_1d",
        }

    monkeypatch.setattr(favorites, "_run_favorite_optimization", fake_run_favorite_optimization)

    with SessionLocal() as db:
        created = _create(
            db,
            name="ALPHA Descoberta",
            symbol="ALPHA/USDT",
            metrics=_discovery_metrics(),
            tier=3,
            start_date="2020-10-10",
            end_date="2024-02-01",
        )
        response = asyncio.run(
            favorites.get_favorite_trades(created.id, current_user_id="user-a", db=db)
        )
        stored = db.query(favorites.FavoriteStrategy).filter_by(id=created.id).one().metrics
        listed = favorites.list_favorites(current_user_id="user-a", db=db)

    assert response.regenerated is True
    assert len(response.trades) == 12
    assert stored["trades_history_cached"] is True
    assert len(stored["trades"]) == 12
    assert stored["sharpe_ratio"] == pytest.approx(0.31)
    assert stored["total_trades"] == 30
    assert stored["win_rate"] == pytest.approx(0.467)
    assert stored["total_return_pct"] == 16951
    assert stored["max_drawdown"] == pytest.approx(0.165)
    assert stored["origin_type"] == "discovery_sweep"
    assert stored["metrics_snapshot"]["total_trades"] == 30
    row = next(item for item in listed if item.id == created.id)
    assert row.metrics["total_trades"] == 30
    assert row.metrics["sharpe_ratio"] == pytest.approx(0.31)
    assert response.metrics["total_trades"] == 30
    assert response.metrics["max_drawdown"] == pytest.approx(0.165)
