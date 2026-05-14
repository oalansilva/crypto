from __future__ import annotations

import pandas as pd

from app.services import combo_optimizer


class _FakeProvider:
    def fetch_ohlcv(self, **_kwargs):
        return pd.DataFrame(
            {
                "open": [100.0, 101.0],
                "high": [102.0, 103.0],
                "low": [99.0, 98.0],
                "close": [101.0, 102.0],
                "volume": [10.0, 11.0],
            },
            index=pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True),
        )


class _FakeStrategy:
    def generate_signals(self, df):
        out = df.copy()
        out["signal"] = [1, -1]
        return out


class _FakeExecutor:
    def __init__(self, *_args, **_kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_optimizer_final_backtest_uses_requested_deep_mode(monkeypatch):
    optimizer = combo_optimizer.ComboOptimizer()
    calls = []

    monkeypatch.setattr(
        optimizer,
        "generate_stages",
        lambda **_kwargs: [{"param": "stop_loss", "values": [0.02]}],
    )
    monkeypatch.setattr(
        optimizer,
        "_execute_opt_stages",
        lambda *args, **_kwargs: (
            {"direction": "long", "stop_loss": 0.02},
            {"sharpe_ratio": 1.0, "total_trades": 1},
        ),
    )
    monkeypatch.setattr(
        optimizer.combo_service,
        "get_template_metadata",
        lambda _template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.02,
            "optimization_schema": {},
        },
    )
    monkeypatch.setattr(
        optimizer.combo_service,
        "create_strategy",
        lambda **_kwargs: _FakeStrategy(),
    )
    monkeypatch.setattr(
        combo_optimizer, "get_market_data_provider", lambda _source: _FakeProvider()
    )
    monkeypatch.setattr(combo_optimizer.concurrent.futures, "ProcessPoolExecutor", _FakeExecutor)

    def fake_extract_trades_with_mode(*_args, **kwargs):
        calls.append(kwargs)
        return (
            [
                {
                    "entry_time": "2026-01-01T00:00:00+00:00",
                    "entry_price": 100.0,
                    "exit_time": "2026-01-01T12:00:00+00:00",
                    "exit_price": 98.0,
                    "profit": -0.02,
                    "exit_reason": "stop_loss_15m",
                }
            ],
            "deep_15m",
        )

    monkeypatch.setattr(combo_optimizer, "extract_trades_with_mode", fake_extract_trades_with_mode)

    result = optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol="BTC/USDT",
        timeframe="1d",
        start_date="2026-01-01",
        end_date="2026-01-02",
        deep_backtest=True,
    )

    assert calls[-1]["deep_backtest"] is True
    assert calls[-1]["return_mode"] is True
    assert result["execution_mode"] == "deep_15m"
    assert result["trades"][0]["exit_reason"] == "stop_loss_15m"
