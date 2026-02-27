from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
import httpx

from app.routes import external_balances


class _FakeResponse:
    def __init__(self, payload: Any):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(external_balances.router)
    return app


async def test_binance_balances_returns_sorted_payload(monkeypatch):
    # Patch env + urllib calls inside services.
    import os
    import urllib.request

    os.environ["BINANCE_API_KEY"] = "k"
    os.environ["BINANCE_API_SECRET"] = "s"

    account_payload = {
        "balances": [
            {"asset": "USDT", "free": "0.1", "locked": "0"},
            {"asset": "HBAR", "free": "0.0", "locked": "10"},
            {"asset": "DUST", "free": "0", "locked": "0"},
        ]
    }

    prices_payload = [
        {"symbol": "HBARUSDT", "price": "0.1"},
        {"symbol": "BTCUSDT", "price": "50000"},
    ]

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "ticker/price" in url:
            return _FakeResponse(prices_payload)
        return _FakeResponse(account_payload)

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    app = _build_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/external/binance/spot/balances")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "balances" in data
    assert "total_usd" in data

    # Should filter out zero totals and sort by value desc:
    # HBAR: 10 * 0.1 = 1.0
    # USDT: 0.1 * 1 = 0.1
    assert [b["asset"] for b in data["balances"]] == ["HBAR", "USDT"]
    assert data["balances"][0]["total"] == 10.0
    assert data["balances"][0]["price_usdt"] == 0.1
    assert data["balances"][0]["value_usd"] == 1.0
    assert data["total_usd"] == 1.1


async def test_binance_balances_missing_secret_returns_400(monkeypatch):
    import os

    os.environ.pop("BINANCE_API_KEY", None)
    os.environ.pop("BINANCE_API_SECRET", None)

    app = _build_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/external/binance/spot/balances")

    assert resp.status_code == 400, resp.text
    assert "Missing Binance credentials" in resp.json()["detail"]


async def test_binance_balances_lookback_days_validation(monkeypatch):
    """Regression: query param must be within 1..3650."""

    import os
    import urllib.request

    os.environ["BINANCE_API_KEY"] = "k"
    os.environ["BINANCE_API_SECRET"] = "s"

    # Minimal payload to avoid extra complexity.
    account_payload = {"balances": [{"asset": "USDT", "free": "1", "locked": "0"}]}
    prices_payload = []

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "ticker/price" in url:
            return _FakeResponse(prices_payload)
        return _FakeResponse(account_payload)

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    app = _build_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp0 = await client.get("/api/external/binance/spot/balances?lookback_days=0")
        resp_hi = await client.get("/api/external/binance/spot/balances?lookback_days=3651")
        resp_ok_lo = await client.get("/api/external/binance/spot/balances?lookback_days=1")
        resp_ok_hi = await client.get("/api/external/binance/spot/balances?lookback_days=3650")

    assert resp0.status_code == 400, resp0.text
    assert "between 1 and 3650" in resp0.json()["detail"]

    assert resp_hi.status_code == 400, resp_hi.text
    assert "between 1 and 3650" in resp_hi.json()["detail"]

    assert resp_ok_lo.status_code == 200, resp_ok_lo.text
    assert resp_ok_hi.status_code == 200, resp_ok_hi.text


async def test_binance_balances_respects_max_symbols_and_time_budget(monkeypatch):
    """Regression: safeguards should stop trade-history lookups and keep response usable."""

    import os
    import urllib.request
    import importlib

    os.environ["BINANCE_API_KEY"] = "k"
    os.environ["BINANCE_API_SECRET"] = "s"

    # Force tiny budgets so we can assert graceful cutoff.
    os.environ["BINANCE_MAX_TRADE_SYMBOLS"] = "10"
    os.environ["BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS"] = "1"

    # Provide 3 non-dust positions with deterministic sorting.
    account_payload = {
        "balances": [
            {"asset": "AAA", "free": "1", "locked": "0"},
            {"asset": "BBB", "free": "1", "locked": "0"},
            {"asset": "CCC", "free": "1", "locked": "0"},
        ]
    }
    prices_payload = [
        {"symbol": "AAAUSDT", "price": "3"},
        {"symbol": "BBBUSDT", "price": "2"},
        {"symbol": "CCCUSDT", "price": "1"},
    ]

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "ticker/price" in url:
            return _FakeResponse(prices_payload)
        return _FakeResponse(account_payload)

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    # Patch compute_avg_buy_cost_usdt and time.time to simulate budget exhaustion after first lookup.
    binance_spot = importlib.import_module("app.services.binance_spot")

    calls = {"n": 0}

    def _fake_avg_cost(asset: str, *, lookback_days=None):
        # Simulate a slow trade-history call so overall lookup budget kicks in.
        import time as _t

        calls["n"] += 1
        _t.sleep(1.2)
        return 1.0

    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", _fake_avg_cost)

    app = _build_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/external/binance/spot/balances")

    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Sorted desc by value: AAA (3), BBB (2), CCC (1)
    assert [b["asset"] for b in data["balances"]] == ["AAA", "BBB", "CCC"]

    # Only the first row should have trade-history-derived fields filled; rest should remain None.
    assert calls["n"] == 1
    assert data["balances"][0]["avg_cost_usdt"] is not None
    assert data["balances"][1]["avg_cost_usdt"] is None
    assert data["balances"][2]["avg_cost_usdt"] is None
