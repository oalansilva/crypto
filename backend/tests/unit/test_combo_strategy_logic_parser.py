import pandas as pd
import pytest

from app.strategies.combos.combo_strategy import ComboStrategy


def _sample_ohlcv(rows: int = 80) -> pd.DataFrame:
    index = pd.date_range("2025-01-01", periods=rows, freq="D", tz="UTC")
    close = pd.Series([100 + (i * 0.7) + ((i % 5) - 2) for i in range(rows)], index=index)
    return pd.DataFrame(
        {
            "timestamp": [int(ts.timestamp() * 1000) for ts in index],
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + 2,
            "low": close - 2,
            "close": close,
            "volume": [1000 + (i * 10) for i in range(rows)],
        },
        index=index,
    )


def test_logic_parser_accepts_macd_dotted_fields():
    strategy = ComboStrategy(
        indicators=[
            {"type": "macd", "alias": "macd", "params": {"fast": 5, "slow": 12, "signal": 4}}
        ],
        entry_logic="macd.macd > macd.signal",
        exit_logic="macd.histogram < 0",
    )

    df = strategy.calculate_indicators(_sample_ohlcv())

    entry = strategy._evaluate_logic_vectorized(df, strategy.entry_logic)
    exit_ = strategy._evaluate_logic_vectorized(df, strategy.exit_logic)

    assert len(entry) == len(df)
    assert len(exit_) == len(df)
    assert entry.dtype == bool
    assert exit_.dtype == bool


def test_logic_parser_accepts_shift_and_abs_series_methods():
    strategy = ComboStrategy(
        indicators=[{"type": "ema", "alias": "trend", "params": {"length": 10}}],
        entry_logic="((close - trend).abs() / trend < 0.05) & (close > close.shift(1))",
        exit_logic="close < trend",
    )

    df = strategy.calculate_indicators(_sample_ohlcv())
    entry = strategy._evaluate_logic_vectorized(df, strategy.entry_logic)

    assert len(entry) == len(df)
    assert entry.dtype == bool


def test_logic_parser_rejects_unsupported_series_methods():
    strategy = ComboStrategy(
        indicators=[],
        entry_logic="close.ewm(span=3).mean() > close",
        exit_logic="close < close.shift(1)",
    )

    with pytest.raises(RuntimeError, match="unknown columns/functions: ewm|Logic references"):
        strategy._evaluate_logic_vectorized(_sample_ohlcv(), strategy.entry_logic)
