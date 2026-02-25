import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import arbitrage_spread_service


@pytest.fixture()
def client():
    return TestClient(app)


def test_arbitrage_spreads_endpoint_returns_payload(monkeypatch, client):
    async def fake_get_spread_opportunities(symbol, exchanges, threshold_pct, timeout_sec=10):
        return {
            "spreads": [
                {
                    "buy_exchange": "binance",
                    "sell_exchange": "okx",
                    "buy_price": 1.0,
                    "sell_price": 1.003,
                    "spread_pct": 0.3,
                    "timestamp": 123,
                    "meets_threshold": True,
                }
            ],
            "opportunities": [
                {
                    "buy_exchange": "binance",
                    "sell_exchange": "okx",
                    "buy_price": 1.0,
                    "sell_price": 1.003,
                    "spread_pct": 0.3,
                    "timestamp": 123,
                    "meets_threshold": True,
                }
            ],
        }

    monkeypatch.setattr(
        arbitrage_spread_service,
        "get_spread_opportunities",
        fake_get_spread_opportunities,
    )

    response = client.get("/api/arbitrage/spreads?exchanges=binance,okx&threshold=0.2&symbols=USDT/USDC")
    assert response.status_code == 200

    payload = response.json()
    assert payload["symbols"] == ["USDT/USDC"]
    assert payload["threshold"] == 0.2
    assert payload["exchanges"] == ["binance", "okx"]
    assert payload["results"]["USDT/USDC"]["spreads"][0]["spread_pct"] == pytest.approx(0.3)
    assert payload["results"]["USDT/USDC"]["opportunities"][0]["spread_pct"] == pytest.approx(0.3)
