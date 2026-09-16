"""Unit tests for operational favorite period after walk-forward (card #949)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.discovery_favorite_metrics import flatten_discovery_grid_metrics
from app.services.favorite_operational_period import (
    OPERATIONAL_PERIOD_FLAG,
    apply_operational_period_to_metrics,
    resolve_chosen_period,
)


def test_resolve_chosen_period_all_uses_today_end(monkeypatch):
    monkeypatch.setattr(
        "app.services.favorite_operational_period._first_candle_iso",
        lambda symbol, timeframe: "2017-08-17",
    )
    now = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
    ptype, start, end = resolve_chosen_period(
        period_type="all",
        start_date=None,
        end_date=None,
        symbol="BTC/USDT",
        timeframe="1d",
        now=now,
    )
    assert ptype == "all"
    assert start == "2017-08-17"
    assert end == "2026-09-15"


def test_resolve_chosen_period_explicit_dates_without_type_is_custom():
    ptype, start, end = resolve_chosen_period(
        period_type=None,
        start_date="2024-01-01",
        end_date="2024-06-30",
        symbol="BTC/USDT",
        timeframe="1d",
    )
    assert ptype is None
    assert start == "2024-01-01"
    assert end == "2024-06-30"


def test_resolve_chosen_period_two_years_not_all():
    now = datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc)
    ptype, start, end = resolve_chosen_period(
        period_type="2y",
        start_date=None,
        end_date=None,
        symbol="ETH/USDT",
        timeframe="1d",
        now=now,
    )
    assert ptype == "2y"
    assert start == "2024-09-15"
    assert end == "2026-09-15"


def test_flatten_skips_operational_discovery_metrics():
    stored = {
        "origin_type": "discovery_sweep",
        "metrics_snapshot": {"total_trades": 30, "sharpe_ratio": 0.31},
        "total_trades": 71,
        "sharpe_ratio": 0.38,
        OPERATIONAL_PERIOD_FLAG: True,
    }
    flat = flatten_discovery_grid_metrics(stored)
    assert flat["total_trades"] == 71
    assert flat["sharpe_ratio"] == 0.38


def test_apply_operational_period_keeps_portrait():
    portrait = {"total_trades": 30, "sharpe_ratio": 0.31}
    operational = {"total_trades": 71, "sharpe_ratio": 0.38, "total_return_pct": 210.4}
    out = apply_operational_period_to_metrics(
        {"origin_type": "discovery_sweep"},
        operational=operational,
        portrait=portrait,
    )
    assert out["metrics_snapshot"] == portrait
    assert out["total_trades"] == 71
    assert out[OPERATIONAL_PERIOD_FLAG] is True
