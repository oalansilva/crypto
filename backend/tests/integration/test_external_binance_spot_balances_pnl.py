import importlib

import pytest


def _set_env(monkeypatch, **kwargs):
    for k, v in kwargs.items():
        monkeypatch.setenv(k, v)


def test_balances_snapshot_includes_avg_cost_and_pnl(monkeypatch):
    """Validate that the balances snapshot includes avg_cost_usdt/pnl fields when trades exist.

    We mock network calls so no real Binance secrets/endpoints are used.
    """

    _set_env(monkeypatch, BINANCE_API_KEY="test", BINANCE_API_SECRET="test", BINANCE_BASE_URL="https://example.invalid")

    # Import modules fresh so env vars are picked up.
    binance_spot = importlib.import_module("app.services.binance_spot")
    binance_trades = importlib.import_module("app.services.binance_trades")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s: int):
        assert path == "/api/v3/account"
        assert timeout_s
        return {
            "balances": [
                {"asset": "ABC", "free": "2", "locked": "0"},
            ]
        }

    def fake_fetch_all_prices():
        return {"ABCUSDT": 2.5}

    def fake_compute_usdt_price(asset, symbol_prices):
        return 2.5

    def fake_fetch_my_trades(symbol: str, *, limit: int = 1000, lookback_days=None):
        assert symbol == "ABCUSDT"
        assert limit
        return [
            {"isBuyer": True, "qty": "2", "price": "2"},
        ]

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", fake_fetch_all_prices)
    monkeypatch.setattr(binance_spot, "compute_usdt_price_for_asset", fake_compute_usdt_price)
    monkeypatch.setattr(binance_trades, "fetch_my_trades", fake_fetch_my_trades)

    out = binance_spot.fetch_spot_balances_snapshot()
    assert "balances" in out
    assert out["balances"][0]["asset"] == "ABC"
    assert out["balances"][0]["avg_cost_usdt"] == pytest.approx(2.0)
    assert out["balances"][0]["pnl_usd"] == pytest.approx((2.5 - 2.0) * 2.0)
    assert out["balances"][0]["pnl_pct"] == pytest.approx(((2.5 / 2.0) - 1.0) * 100.0)
