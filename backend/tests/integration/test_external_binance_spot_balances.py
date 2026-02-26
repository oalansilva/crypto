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
