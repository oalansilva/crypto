"""Slippage table for Discovery swing timeframes (card #1074)."""

from app.metrics.backtest_execution_costs import (
    TRADING_FEE,
    fees_slippage_record,
    long_trade_profit_frac,
    slippage_for_timeframe,
)


def test_slippage_for_timeframe_table():
    assert slippage_for_timeframe("1d") == 0.0002
    assert slippage_for_timeframe("4h") == 0.0002
    assert slippage_for_timeframe("1h") == 0.0003
    assert slippage_for_timeframe("15m") == 0.0005
    assert slippage_for_timeframe("5m") == 0.0
    assert slippage_for_timeframe(None) == 0.0


def test_fees_slippage_record_uses_trading_fee():
    rec = fees_slippage_record("1h")
    assert rec["fees"] == TRADING_FEE
    assert rec["slippage"] == 0.0003


def test_long_trade_profit_lower_with_higher_slippage():
    entry, exit_ = 100.0, 110.0
    fee_only = long_trade_profit_frac(entry, exit_, fee=TRADING_FEE, slippage=0.0)
    with_1h = long_trade_profit_frac(entry, exit_, fee=TRADING_FEE, slippage=0.0003)
    with_15m = long_trade_profit_frac(entry, exit_, fee=TRADING_FEE, slippage=0.0005)
    assert with_1h < fee_only
    assert with_15m < with_1h
    assert fee_only - with_1h > 0
    assert with_1h - with_15m > 0


def test_1d_4h_use_two_basis_point_slippage():
    assert fees_slippage_record("1d")["slippage"] == 0.0002
    assert fees_slippage_record("4h")["slippage"] == 0.0002


def test_run_optimization_final_and_holdout_apply_timeframe_slippage(monkeypatch):
    import pandas as pd

    from app.services import combo_optimizer

    optimizer = combo_optimizer.ComboOptimizer()
    slippage_calls: list[float] = []

    class _FakeStrategy:
        def generate_signals(self, df):
            out = df.copy()
            signals = [0] * len(out)
            if len(signals) >= 2:
                signals[0] = 1
                signals[1] = -1
            out["signal"] = signals
            return out

    def _fake_extract(*_args, **kwargs):
        slippage_calls.append(float(kwargs.get("slippage", 0.0)))
        slip = float(kwargs.get("slippage", 0.0))
        entry, exit_ = 100.0, 110.0
        profit_with_slip = long_trade_profit_frac(entry, exit_, fee=TRADING_FEE, slippage=slip)
        profit_fee_only = long_trade_profit_frac(entry, exit_, fee=TRADING_FEE, slippage=0.0)
        assert profit_with_slip < profit_fee_only
        return (
            [
                {
                    "entry_time": "2026-01-01T00:00:00+00:00",
                    "entry_price": entry,
                    "exit_time": "2026-01-01T12:00:00+00:00",
                    "exit_price": exit_,
                    "profit": profit_with_slip,
                    "exit_reason": "signal",
                }
            ],
            "fast_1h",
        )

    ohlcv = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.5, 101.5, 102.5, 103.5],
            "volume": [10.0, 11.0, 12.0, 13.0],
        },
        index=pd.date_range("2026-01-01", periods=4, freq="1h", tz="UTC"),
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
    class _FakeProvider:
        def fetch_ohlcv(self, **_kwargs):
            return ohlcv

    class _FakeExecutor:
        def __init__(self, *_args, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(combo_optimizer, "get_market_data_provider", lambda _source: _FakeProvider())
    monkeypatch.setattr(combo_optimizer.concurrent.futures, "ProcessPoolExecutor", _FakeExecutor)
    monkeypatch.setattr(combo_optimizer, "extract_trades_with_mode", _fake_extract)

    optimizer.run_optimization(
        template_name="multi_ma_crossover",
        symbol="BTC/USDT",
        timeframe="1h",
        start_date="2026-01-01",
        end_date="2026-01-02",
        deep_backtest=False,
        split_train_ratio=0.5,
    )

    assert slippage_calls
    assert all(s == slippage_for_timeframe("1h") for s in slippage_calls)
    assert slippage_for_timeframe("1h") == 0.0003
    assert slippage_for_timeframe("15m") > slippage_for_timeframe("1h")
