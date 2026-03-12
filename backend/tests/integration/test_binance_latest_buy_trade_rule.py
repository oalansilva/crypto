from app.services.binance_trades import compute_avg_buy_cost_usdt_for_symbol


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
