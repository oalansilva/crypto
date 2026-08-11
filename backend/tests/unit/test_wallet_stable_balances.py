import importlib

import pytest


def test_compute_usdt_price_for_stable_assets_without_ticker():
    prices = importlib.import_module("app.services.binance_prices")
    empty = {}
    assert prices.compute_usdt_price_for_asset("USDT", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("USDC", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("BUSD", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("FDUSD", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("LDUSDT", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("LDUSDC", empty) == 1.0
    assert prices.compute_usdt_price_for_asset("UNKNOWN", empty) is None


def test_balances_snapshot_lists_earn_ld_stables(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    monkeypatch.setattr(
        binance_spot,
        "_signed_get",
        lambda *a, **k: {
            "balances": [
                {"asset": "LDUSDC", "free": "350.24", "locked": "0"},
                {"asset": "LDUSDT", "free": "89.83", "locked": "0"},
                {"asset": "ETH", "free": "0.05", "locked": "0"},
            ]
        },
    )
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {"ETHUSDT": 2000.0})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: 1800.0)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s")
    assets = [row["asset"] for row in out["balances"]]
    assert "LDUSDC" in assets
    assert "LDUSDT" in assets
    ldusdc = next(r for r in out["balances"] if r["asset"] == "LDUSDC")
    assert ldusdc["price_usdt"] == 1.0
    assert ldusdc["value_usd"] == pytest.approx(350.24)
    assert out["total_usd"] == pytest.approx(350.24 + 89.83 + 100.0)


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


def test_balances_snapshot_prefers_simple_earn_over_ld_wrappers(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        if path == "/api/v3/account":
            return {
                "balances": [
                    {"asset": "LDUSDC", "free": "350.24", "locked": "0"},
                    {"asset": "LDUSDT", "free": "89.83", "locked": "0"},
                    {"asset": "ETH", "free": "0.05", "locked": "0"},
                ]
            }
        if path == "/sapi/v1/simple-earn/flexible/position":
            return {
                "rows": [
                    {"asset": "USDC", "totalAmount": "387.17788437"},
                    {"asset": "USDT", "totalAmount": "101.79216207"},
                ]
            }
        if path == "/sapi/v1/simple-earn/locked/position":
            return {"rows": []}
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {"ETHUSDT": 2000.0})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: 1800.0)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s")
    assets = [row["asset"] for row in out["balances"]]
    assert "LDUSDC" not in assets
    assert "LDUSDT" not in assets
    assert "USDC" in assets
    assert "USDT" in assets

    usdc = next(r for r in out["balances"] if r["asset"] == "USDC")
    usdt = next(r for r in out["balances"] if r["asset"] == "USDT")
    assert usdc["total"] == pytest.approx(387.17788437)
    assert usdt["total"] == pytest.approx(101.79216207)
    assert out["total_usd"] == pytest.approx(387.17788437 + 101.79216207 + 100.0)


def test_balances_snapshot_keeps_earn_out_of_free_and_exposes_earn_amount(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        if path == "/api/v3/account":
            return {
                "balances": [
                    {"asset": "USDT", "free": "0.65270319", "locked": "0"},
                    {"asset": "LDUSDT", "free": "100.00", "locked": "0"},
                ]
            }
        if path == "/sapi/v1/simple-earn/flexible/position":
            return {"rows": [{"asset": "USDT", "totalAmount": "100.00"}]}
        if path == "/sapi/v1/simple-earn/locked/position":
            return {"rows": []}
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: None)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s", min_usd=0)
    usdt = next(r for r in out["balances"] if r["asset"] == "USDT")
    assert usdt["free"] == pytest.approx(0.65270319)
    assert usdt["total"] == pytest.approx(100.65270319)
    assert usdt["earn_amount"] == pytest.approx(100.00)
    assert out["total_usd"] == pytest.approx(100.65270319)


def test_balances_snapshot_earn_amount_zero_when_no_earn(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        if path == "/api/v3/account":
            return {"balances": [{"asset": "USDT", "free": "50", "locked": "0"}]}
        if path == "/sapi/v1/simple-earn/flexible/position":
            return {"rows": []}
        if path == "/sapi/v1/simple-earn/locked/position":
            return {"rows": []}
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: None)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s", min_usd=0)
    usdt = next(r for r in out["balances"] if r["asset"] == "USDT")
    assert usdt["free"] == pytest.approx(50)
    assert usdt["total"] == pytest.approx(50)
    assert usdt["earn_amount"] == pytest.approx(0)


def test_balances_snapshot_skips_non_stable_ld_when_earn_lists_base(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        if path == "/api/v3/account":
            return {
                "balances": [
                    {"asset": "ETH", "free": "0", "locked": "0.0519"},
                    {"asset": "LDETH", "free": "0.00010579", "locked": "0"},
                ]
            }
        if path == "/sapi/v1/simple-earn/flexible/position":
            return {"rows": [{"asset": "ETH", "totalAmount": "0.00010955"}]}
        if path == "/sapi/v1/simple-earn/locked/position":
            return {"rows": []}
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {"ETHUSDT": 2000.0})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: 1800.0)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s", min_usd=0)
    assets = [row["asset"] for row in out["balances"]]
    assert "LDETH" not in assets
    assert "ETH" in assets
    eth = next(r for r in out["balances"] if r["asset"] == "ETH")
    assert eth["total"] == pytest.approx(0.0519 + 0.00010955)


def test_balances_snapshot_falls_back_to_ld_when_earn_api_fails(monkeypatch):
    binance_spot = importlib.import_module("app.services.binance_spot")

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        if path == "/api/v3/account":
            return {
                "balances": [
                    {"asset": "LDUSDC", "free": "350.24", "locked": "0"},
                    {"asset": "LDUSDT", "free": "89.83", "locked": "0"},
                ]
            }
        if path.startswith("/sapi/v1/simple-earn/"):
            raise RuntimeError("earn unavailable")
        raise AssertionError(f"unexpected path: {path}")

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {})
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", lambda *a, **k: None)

    out = binance_spot.fetch_spot_balances_snapshot(api_key="k", api_secret="s")
    assets = [row["asset"] for row in out["balances"]]
    assert "LDUSDC" in assets
    assert "LDUSDT" in assets
    assert "USDC" not in assets
    assert out["total_usd"] == pytest.approx(350.24 + 89.83)
