"""Fixtures partilhadas da suíte de integração backend."""

from __future__ import annotations

import pytest


def _enrich_without_backtest(**kwargs):
    """Resolve período operacional sem ComboOptimizer/OHLCV (transacção Postgres curta)."""
    from app.services.favorite_operational_period import resolve_chosen_period

    metrics = dict(kwargs.get("metrics") or {})
    ptype, start, end = resolve_chosen_period(
        period_type=kwargs.get("period_type"),
        start_date=kwargs.get("start_date"),
        end_date=kwargs.get("end_date"),
        symbol=kwargs.get("symbol"),
        timeframe=kwargs.get("timeframe"),
    )
    return ptype, start, end, metrics


@pytest.fixture(autouse=True)
def _integration_isolate_oos_backtest(monkeypatch, request):
    """Evita backtest real entre lock_and_find_duplicate e commit (lock wait entre testes)."""
    if request.node.get_closest_marker("integration_real_oos_enrich"):
        return

    monkeypatch.setattr(
        "app.services.favorite_operational_period._first_candle_iso",
        lambda symbol, timeframe: "2017-08-17",
    )
    monkeypatch.setattr(
        "app.services.favorite_operational_period.enrich_walk_forward_favorite_create",
        _enrich_without_backtest,
    )
