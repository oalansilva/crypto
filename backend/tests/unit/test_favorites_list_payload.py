from app.routes import favorites as favorites_routes


def test_metrics_for_favorites_list_strips_heavy_series():
    metrics = {
        "total_trades": 3,
        "total_return": 0.42,
        "analysis_candles": [{"timestamp_utc": "2026-01-01T00:00:00Z", "close": 1}],
        "analysis_indicator_data": {"fast": [1, 2, 3]},
        "analysis_strategy_transparency": {"display_name": "Test"},
        "trades": [{"entry_time": "2026-01-01T00:00:00Z"}],
    }

    slim = favorites_routes._metrics_for_favorites_list(metrics)

    assert slim["total_trades"] == 3
    assert slim["total_return"] == 0.42
    assert "analysis_candles" not in slim
    assert "analysis_indicator_data" not in slim
    assert "analysis_strategy_transparency" not in slim
    assert "trades" not in slim
