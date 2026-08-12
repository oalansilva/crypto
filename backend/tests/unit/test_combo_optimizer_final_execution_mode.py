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
    intraday_df = pd.DataFrame(
        {
            "open": [100.0],
            "high": [101.0],
            "low": [99.0],
            "close": [100.5],
            "volume": [1.0],
        },
        index=pd.to_datetime(["2026-01-02T00:00:00Z"]),
    )

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
    monkeypatch.setattr(optimizer.loader, "fetch_intraday_data", lambda **_kwargs: intraday_df)
    monkeypatch.setattr(
        optimizer.loader,
        "check_intraday_availability",
        lambda *_args, **_kwargs: {
            "available": True,
            "coverage": {"end": "2026-01-02T00:00:00+00:00"},
        },
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


def test_optimizer_final_backtest_preserves_requested_short_direction(monkeypatch):
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
            {"direction": "short", "stop_loss": 0.02},
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
        optimizer.combo_service, "create_strategy", lambda **_kwargs: _FakeStrategy()
    )
    monkeypatch.setattr(
        combo_optimizer, "get_market_data_provider", lambda _source: _FakeProvider()
    )
    monkeypatch.setattr(
        combo_optimizer.concurrent.futures,
        "ProcessPoolExecutor",
        _FakeExecutor,
    )

    def fake_extract_trades_with_mode(*_args, **kwargs):
        calls.append(kwargs)
        return (
            [
                {
                    "entry_time": "2026-01-01T00:00:00+00:00",
                    "entry_price": 100.0,
                    "exit_time": "2026-01-02T00:00:00+00:00",
                    "exit_price": 90.0,
                    "profit": 0.1,
                    "exit_reason": "signal",
                    "type": kwargs["direction"],
                }
            ],
            "fast_1d",
        )

    monkeypatch.setattr(combo_optimizer, "extract_trades_with_mode", fake_extract_trades_with_mode)

    result = optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol="BTC/USDT",
        timeframe="1d",
        start_date="2026-01-01",
        end_date="2026-01-02",
        direction="short",
        deep_backtest=False,
    )

    assert calls[-1]["direction"] == "short"
    assert result["direction"] == "short"
    assert result["trades"][0]["type"] == "short"


def test_optimizer_split_produces_holdout_verdict_with_go_metrics(monkeypatch):
    """Walk-forward (card #470): com split, o resultado contém oos_metrics com
    cagr/calmar/benchmark e oos_verdict calculado pelo gate real."""
    optimizer = combo_optimizer.ComboOptimizer()
    n_candles = 60
    dates = pd.date_range("2025-01-01", periods=n_candles, freq="D")
    full_df = pd.DataFrame(
        {
            "open": [100.0] * n_candles,
            "high": [102.0] * n_candles,
            "low": [99.0] * n_candles,
            "close": [100.0 + i * 0.5 for i in range(n_candles)],
            "volume": [10.0] * n_candles,
        },
        index=pd.to_datetime(dates, utc=True),
    )

    class _FullProvider:
        def fetch_ohlcv(self, **_kwargs):
            return full_df.copy()

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
            {"sharpe_ratio": 1.0, "total_trades": 5},
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
        combo_optimizer, "get_market_data_provider", lambda _source: _FullProvider()
    )
    monkeypatch.setattr(
        optimizer.loader,
        "check_intraday_availability",
        lambda *_args, **_kwargs: {
            "available": True,
            "coverage": {"end": str(full_df.index.max())},
        },
    )
    monkeypatch.setattr(combo_optimizer.concurrent.futures, "ProcessPoolExecutor", _FakeExecutor)

    class _SizedStrategy:
        def generate_signals(self, df):
            out = df.copy()
            out["signal"] = [1 if i % 2 == 0 else -1 for i in range(len(out))]
            return out

    monkeypatch.setattr(
        optimizer.combo_service,
        "create_strategy",
        lambda **_kwargs: _SizedStrategy(),
    )

    fake_trades = [
        {
            "entry_time": str(full_df.index[i].isoformat()),
            "entry_price": 100.0,
            "exit_time": str(full_df.index[i + 1].isoformat()),
            "exit_price": 102.0,
            "profit": 0.02,
            "exit_reason": "signal",
        }
        for i in range(0, 20)
    ]

    def fake_extract(*_args, **kwargs):
        return list(fake_trades), "fast_1d"

    monkeypatch.setattr(combo_optimizer, "extract_trades_with_mode", fake_extract)

    result = optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol="BTC/USDT",
        timeframe="1d",
        start_date="2025-01-01",
        end_date=str(full_df.index.max().date()),
        direction="long",
        deep_backtest=False,
        split_train_ratio=0.7,
    )

    assert result["oos_metrics"] is not None
    assert "cagr" in result["oos_metrics"]
    assert "calmar_ratio" in result["oos_metrics"]
    assert "benchmark" in result["oos_metrics"]
    assert result["oos_verdict"] is not None
    assert "status" in result["oos_verdict"]
    assert "split_train_ratio" in result["oos_verdict"]
