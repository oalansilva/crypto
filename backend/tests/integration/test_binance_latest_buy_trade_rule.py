from app.services.binance_trades import (
    compute_avg_buy_cost_usdt,
    compute_avg_buy_cost_usdt_for_symbol,
)


def test_compute_avg_buy_cost_uses_latest_buy_trade_price():
    trades = [
        {"isBuyer": True, "qty": "10", "price": "0.08", "time": 1000},
        {"isBuyer": False, "qty": "3", "price": "0.20", "time": 1500},
        {"isBuyer": True, "qty": "5", "price": "0.11", "time": 2000},
        {"isBuyer": True, "qty": "7", "price": "0.14", "time": 3000},
    ]

    assert compute_avg_buy_cost_usdt_for_symbol("HBARUSDT", trades) == 0.14


def test_compute_avg_buy_cost_falls_back_to_last_valid_buy_when_time_missing():
    trades = [
        {"isBuyer": True, "qty": "10", "price": "1.0"},
        {"isBuyer": True, "qty": "0", "price": "9.0"},
        {"isBuyer": True, "qty": "3", "price": "1.5"},
    ]

    assert compute_avg_buy_cost_usdt_for_symbol("ABCUSDT", trades) == 1.5


def test_compute_avg_buy_cost_prefers_newer_usdc_buy_over_older_usdt(monkeypatch):
    """ETH-like case: real buy on USDC must win over older USDT trade."""

    def fake_fetch(symbol, **kwargs):
        if symbol == "ETHUSDT":
            return [{"isBuyer": True, "qty": "0.05", "price": "2247.87", "time": 1_700_000_000_000}]
        if symbol == "ETHUSDC":
            return [
                {"isBuyer": True, "qty": "0.052", "price": "1920.42", "time": 1_721_080_367_000}
            ]
        return []

    monkeypatch.setattr("app.services.binance_trades.fetch_my_trades", fake_fetch)
    assert compute_avg_buy_cost_usdt("ETH", api_key="k", api_secret="s") == 1920.42


def test_compute_avg_buy_cost_uses_usdt_when_usdc_empty(monkeypatch):
    def fake_fetch(symbol, **kwargs):
        if symbol == "BTCUSDT":
            return [{"isBuyer": True, "qty": "0.01", "price": "65000", "time": 100}]
        return []

    monkeypatch.setattr("app.services.binance_trades.fetch_my_trades", fake_fetch)
    assert compute_avg_buy_cost_usdt("BTC", api_key="k", api_secret="s") == 65000.0


def test_compute_avg_buy_cost_queries_stable_quotes_for_any_asset(monkeypatch):
    seen: list[str] = []

    def fake_fetch(symbol, **kwargs):
        seen.append(symbol)
        return []

    monkeypatch.setattr("app.services.binance_trades.fetch_my_trades", fake_fetch)
    assert compute_avg_buy_cost_usdt("SOL", api_key="k", api_secret="s") is None
    assert compute_avg_buy_cost_usdt("ADA", api_key="k", api_secret="s") is None
    assert seen == ["SOLUSDT", "SOLUSDC", "ADAUSDT", "ADAUSDC"]
