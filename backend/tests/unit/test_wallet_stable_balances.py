import importlib

import pytest


def test_compute_usdt_price_for_stable_assets_without_ticker():
    prices = importlib.import_module("app.services.binance_prices")
    empty = {}
    assert prices.compute_usdt_price_for_asset("USDT", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("USDC", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("BUSD", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("FDUSD", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("UNKNOWN", empty) is None


def test_balances_snapshot_lists_usdt_and_usdc_with_stable_cost(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        return {
            "balances": [
                {"asset": "USDT", "free": "100", "locked": "0"},
                {"asset": "USDC", "free": "50.5", "locked": "0"},
                {"asset": "ETH", "free": "1", "locked": "0"},
                {"asset": "DUSTUSDT", "free": "0.001", "locked": "0"},
            ]
        }

    def fake_price(asset, _prices):
        # ETH has ticker; stables rely on STABLE_ASSETS fallback inside compute or here.
        return {"ETH": 2000.0}.get(asset)

    avg_calls: list[str] = []

    def fake_avg(asset, **kwargs):
        avg_calls.append(asset)
        return 1800.0 if asset == "ETH" else None

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {})
    # Use real price helper path for stables: patch only non-stable via wrapper
    real_price = binance_spot.compute_usdt_price_for_asset

    def price_with_eth(asset, symbol_prices):
        if asset == "ETH":
            return 2000.0
        return real_price(asset, symbol_prices)

    monkeypatch.setattr(binance_spot, "compute_usdt_price_for_asset", price_with_eth)
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", fake_avg)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s")
    assets = [row["asset"] for row in out["balances"]]
    assert "USDT" in assets
    assert "USDC" in assets
    assert "ETH" in assets
    assert "DUSTUSDT" not in assets  # dust under default 0.02 if priced as unknown/null omitted

    usdt = next(r for r in out["balances"] if r["asset"] == "USDT")
    usdc = next(r for r in out["balances"] if r["asset"] == "USDC")
    assert usdt["price_usdt"] == 1.0
    assert usdt["value_usd"] == pytest.approx(100.0)
    assert usdt["avg_cost_usdt"] == 1.0
    assert usdt["pnl_usd"] == 0.0
    assert usdc["value_usd"] == pytest.approx(50.5)
    assert out["total_usd"] == pytest.approx(100.0 + 50.5 + 2000.0)
    # Trade lookups skip stables
    assert avg_calls == ["ETH"]


def test_balances_snapshot_min_usd_zero_includes_small_stable(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    monkeypatch.setattr(
        binance_spot,
        "_signed_get",
        lambda *a, **k: {"balances": [{"asset": "USDC", "free": "0.01", "locked": "0"}]},
    )
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: None)

    hidden = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s")
    assert hidden["balances"] == []

    shown = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s", min_usd=0)
    assert len(shown["balances"]) == 1
    assert shown["balances"][0]["asset"] == "USDC"
    assert shown["total_usd"] == pytest.approx(0.01)
