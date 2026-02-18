import pytest

from app.services.arbitrage_spread_service import calculate_spreads


def test_calculate_spreads_applies_threshold():
    quotes = {
        "binance": {"best_ask": 1.0000, "best_bid": 0.9990, "timestamp": 100},
        "okx": {"best_ask": 1.0020, "best_bid": 1.0030, "timestamp": 120},
    }

    results = calculate_spreads(quotes, threshold_pct=0.2)
    assert len(results["spreads"]) == 2
    assert len(results["opportunities"]) == 1

    opportunity = results["opportunities"][0]
    assert opportunity["buy_exchange"] == "binance"
    assert opportunity["sell_exchange"] == "okx"
    assert opportunity["buy_price"] == pytest.approx(1.0)
    assert opportunity["sell_price"] == pytest.approx(1.003)
    assert opportunity["spread_pct"] == pytest.approx(0.3, abs=1e-3)
