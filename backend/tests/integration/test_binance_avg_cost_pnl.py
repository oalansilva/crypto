from __future__ import annotations

import json
import urllib.parse

from fastapi import FastAPI
import httpx

from app.routes import external_balances


class _FakeResponse:
    def __init__(self, payload):
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


async def test_wallet_returns_avg_cost_and_pnl(monkeypatch):
    import os
    import urllib.request

    os.environ["BINANCE_API_KEY"] = "k"
    os.environ["BINANCE_API_SECRET"] = "s"

    account_payload = {
        "balances": [
            {"asset": "HBAR", "free": "0", "locked": "100"},
        ]
    }
    prices_payload = [
        {"symbol": "HBARUSDT", "price": "0.10"},
        {"symbol": "BTCUSDT", "price": "50000"},
    ]

    # Two buy trades at 0.08 and 0.12, qty 10 each => avg 0.10
    mytrades_payload = [
        {"isBuyer": True, "qty": "10", "price": "0.08"},
        {"isBuyer": True, "qty": "10", "price": "0.12"},
        {"isBuyer": False, "qty": "5", "price": "0.20"},
    ]

    def _fake_urlopen(req, timeout=30):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "ticker/price" in url:
            return _FakeResponse(prices_payload)
        if "/api/v3/myTrades" in url:
            parsed = urllib.parse.urlparse(url)
            q = urllib.parse.parse_qs(parsed.query)
            assert q.get("symbol", [""])[0] == "HBARUSDT"
            return _FakeResponse(mytrades_payload)
        return _FakeResponse(account_payload)

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    app = _build_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/external/binance/spot/balances")

    assert resp.status_code == 200, resp.text
    data = resp.json()
    row = data["balances"][0]
    assert row["asset"] == "HBAR"
    assert row["avg_cost_usdt"] == 0.10
    assert row["pnl_usd"] == 0.0
    assert row["pnl_pct"] == 0.0
