from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@dataclass(frozen=True)
class TradingViewFixture:
    symbol: str
    timeframe: str
    filename: str


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "tradingview"


def _load_reference_df(filename: str) -> pd.DataFrame:
    path = _fixtures_dir() / filename
    df = pd.read_csv(path)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    return df.sort_values("timestamp_utc").reset_index(drop=True)


def _resolve_timeframe_delta(timeframe: str) -> pd.Timedelta:
    mapping = {
        "1m": pd.Timedelta(minutes=1),
        "5m": pd.Timedelta(minutes=5),
        "15m": pd.Timedelta(minutes=15),
        "1h": pd.Timedelta(hours=1),
        "4h": pd.Timedelta(hours=4),
        "1d": pd.Timedelta(days=1),
    }
    return mapping[timeframe]


def _assert_timeframe_regular_and_utc(
    df: pd.DataFrame, timeframe: str, *, require_no_gaps: bool = True
) -> None:
    assert df["timestamp_utc"].dt.tz is not None
    deltas = df["timestamp_utc"].diff().dropna()
    if deltas.empty:
        return

    expected = _resolve_timeframe_delta(timeframe)
    assert deltas.min() >= expected

    if require_no_gaps:
        assert set(deltas.unique()) == {expected}


def _compute_fixture(service, df: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
    input_df = df[["timestamp_utc", "open", "high", "low", "close", "volume"]].rename(
        columns={"timestamp_utc": "ts"}
    )
    return service._compute_indicators(input_df, timeframe=timeframe, symbol=symbol)


def _assert_matching(
    computed: pd.Series,
    expected: pd.Series,
    indicator: str,
    rtol: float,
    atol: float,
) -> None:
    expected_values = expected.to_numpy(dtype=float)
    computed_values = computed.to_numpy(dtype=float)

    valid_mask = ~np.isnan(expected_values)
    if not np.any(valid_mask):
        return

    np.testing.assert_allclose(
        computed_values[valid_mask],
        expected_values[valid_mask],
        rtol=rtol,
        atol=atol,
        err_msg=f"{indicator} diverges beyond tolerance from TradingView fixture",
    )


def _independent_bbands(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    middle = close.rolling(window=20, min_periods=20).mean()
    stddev = close.rolling(window=20, min_periods=20).std(ddof=0)
    return middle + (stddev * 2), middle, middle - (stddev * 2)


def _independent_atr(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)

    period = 14
    values = [np.nan] * len(true_range)
    if len(true_range) > period:
        values[period] = true_range.iloc[1 : period + 1].mean()
        for idx in range(period + 1, len(true_range)):
            values[idx] = ((values[idx - 1] * (period - 1)) + true_range.iloc[idx]) / period
    return pd.Series(values, index=true_range.index, name="atr_14")


def _independent_stoch(
    high: pd.Series, low: pd.Series, close: pd.Series
) -> tuple[pd.Series, pd.Series]:
    lowest_low = low.rolling(window=14, min_periods=14).min()
    highest_high = high.rolling(window=14, min_periods=14).max()
    fast_k = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    slow_k = fast_k.rolling(window=3, min_periods=3).mean()
    slow_d = slow_k.rolling(window=3, min_periods=3).mean()
    return slow_k.where(slow_d.notna()), slow_d


def _independent_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    if close.empty:
        return pd.Series(dtype=float, name="obv")

    values = [float(volume.iloc[0])]
    for idx in range(1, len(close)):
        if close.iloc[idx] > close.iloc[idx - 1]:
            values.append(values[-1] + float(volume.iloc[idx]))
        elif close.iloc[idx] < close.iloc[idx - 1]:
            values.append(values[-1] - float(volume.iloc[idx]))
        else:
            values.append(values[-1])
    return pd.Series(values, index=close.index, name="obv")


def _independent_ichimoku(
    high: pd.Series, low: pd.Series, close: pd.Series
) -> dict[str, pd.Series]:
    def midpoint(period: int) -> pd.Series:
        highest_high = high.rolling(window=period, min_periods=period).max()
        lowest_low = low.rolling(window=period, min_periods=period).min()
        return (highest_high + lowest_low) / 2

    tenkan = midpoint(9)
    kijun = midpoint(26)
    return {
        "ichimoku_tenkan_9": tenkan,
        "ichimoku_kijun_26": kijun,
        "ichimoku_senkou_a_9_26_52": (tenkan + kijun) / 2,
        "ichimoku_senkou_b_9_26_52": midpoint(52),
        "ichimoku_chikou_26": close,
    }


@pytest.mark.parametrize(
    "fixture",
    [
        TradingViewFixture("BTCUSDT", "1d", "btcusdt_1d_tradingview_reference.csv"),
        TradingViewFixture("BTCUSDT", "1h", "btcusdt_1h_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1d", "nvda_1d_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1h", "nvda_1h_tradingview_reference.csv"),
    ],
)
def test_market_indicator_tradingview_fixture_parity_with_tolerance(
    fixture: TradingViewFixture,
) -> None:
    pytest.importorskip("talib", reason="TA-Lib required for indicator parity tests")

    from app.services.market_indicator_service import MarketIndicatorService

    service = MarketIndicatorService()
    df = _load_reference_df(fixture.filename)

    expected_cols = {
        "timestamp_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ema_9",
        "ema_21",
        "sma_20",
        "sma_50",
        "rsi_14",
        "macd_line",
        "macd_signal",
        "macd_histogram",
    }
    assert expected_cols.issubset(df.columns)
    assert df["timestamp_utc"].is_monotonic_increasing

    if df.shape[0] < 70:
        pytest.skip("fixture short for 50-period SMA validation")

    _assert_timeframe_regular_and_utc(df, fixture.timeframe)

    computed = _compute_fixture(service, df, fixture.symbol, fixture.timeframe)

    tolerance_by_indicator = {
        "ema_9": (1e-4, 1e-3),
        "ema_21": (1e-4, 1e-3),
        "sma_20": (1e-4, 1e-3),
        "sma_50": (1e-4, 1e-3),
        "rsi_14": (1e-4, 1e-4),
        "macd_line": (1e-4, 1e-3),
        "macd_signal": (1e-4, 1e-3),
        "macd_histogram": (1e-4, 1e-3),
    }

    for column, (rtol, atol) in tolerance_by_indicator.items():
        _assert_matching(computed[column], df[column], column, rtol=rtol, atol=atol)

    warmup_mask = df["ema_9"].isna() & df["sma_20"].isna() & df["rsi_14"].isna()
    assert warmup_mask.any()


@pytest.mark.parametrize(
    "fixture",
    [
        TradingViewFixture("BTCUSDT", "1d", "btcusdt_1d_tradingview_reference.csv"),
        TradingViewFixture("BTCUSDT", "1h", "btcusdt_1h_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1d", "nvda_1d_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1h", "nvda_1h_tradingview_reference.csv"),
    ],
)
def test_advanced_market_indicators_cross_validate_with_talib_and_formulas(
    fixture: TradingViewFixture,
) -> None:
    talib = pytest.importorskip("talib", reason="TA-Lib required for indicator parity tests")
    pandas_ta = pytest.importorskip("pandas_ta", reason="pandas-ta required for cross-source tests")

    from app.services.market_indicator_service import MarketIndicatorService

    service = MarketIndicatorService()
    df = _load_reference_df(fixture.filename)
    _assert_timeframe_regular_and_utc(df, fixture.timeframe)
    computed = _compute_fixture(service, df, fixture.symbol, fixture.timeframe)

    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)
    volume = df["volume"].astype(float)

    talib_upper, talib_middle, talib_lower = talib.BBANDS(
        close.to_numpy(), timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
    )
    talib_stoch_k, talib_stoch_d = talib.STOCH(
        high.to_numpy(),
        low.to_numpy(),
        close.to_numpy(),
        fastk_period=14,
        slowk_period=3,
        slowk_matype=0,
        slowd_period=3,
        slowd_matype=0,
    )
    talib_expected = {
        "bb_upper_20_2": pd.Series(talib_upper),
        "bb_middle_20_2": pd.Series(talib_middle),
        "bb_lower_20_2": pd.Series(talib_lower),
        "atr_14": pd.Series(talib.ATR(high, low, close, timeperiod=14)),
        "stoch_k_14_3_3": pd.Series(talib_stoch_k),
        "stoch_d_14_3_3": pd.Series(talib_stoch_d),
        "obv": pd.Series(talib.OBV(close, volume)),
    }
    for column, expected in talib_expected.items():
        _assert_matching(computed[column], expected, f"{column} TA-Lib", rtol=1e-10, atol=1e-6)

    pandas_ta_bbands = pandas_ta.bbands(close, length=20, std=2)
    pandas_ta_stoch = pandas_ta.stoch(high, low, close, k=14, d=3, smooth_k=3)
    pandas_ta_expected = {
        "bb_upper_20_2": pandas_ta_bbands["BBU_20_2.0_2.0"],
        "bb_middle_20_2": pandas_ta_bbands["BBM_20_2.0_2.0"],
        "bb_lower_20_2": pandas_ta_bbands["BBL_20_2.0_2.0"],
        "atr_14": pandas_ta.atr(high, low, close, length=14),
        "stoch_k_14_3_3": pandas_ta_stoch["STOCHk_14_3_3"],
        "stoch_d_14_3_3": pandas_ta_stoch["STOCHd_14_3_3"],
        "obv": pandas_ta.obv(close, volume),
    }
    for column, expected in pandas_ta_expected.items():
        _assert_matching(computed[column], expected, f"{column} pandas-ta", rtol=1e-10, atol=1e-6)

    formula_upper, formula_middle, formula_lower = _independent_bbands(close)
    formula_stoch_k, formula_stoch_d = _independent_stoch(high, low, close)
    formula_expected = {
        "bb_upper_20_2": formula_upper,
        "bb_middle_20_2": formula_middle,
        "bb_lower_20_2": formula_lower,
        "atr_14": _independent_atr(high, low, close),
        "stoch_k_14_3_3": formula_stoch_k,
        "stoch_d_14_3_3": formula_stoch_d,
        "obv": _independent_obv(close, volume),
        **_independent_ichimoku(high, low, close),
    }
    for column, expected in formula_expected.items():
        _assert_matching(computed[column], expected, f"{column} formula", rtol=1e-10, atol=1e-6)

    assert computed["source_window"].iloc[-1]["advanced_indicators"]["ichimoku"] == {
        "tenkan": 9,
        "kijun": 26,
        "senkou_b": 52,
        "displacement": 26,
        "storage": "source_candle_aligned",
    }


def test_advanced_market_indicator_upsert_serializes_nullable_values_and_conflict_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("talib", reason="TA-Lib required for indicator parity tests")

    from app.services import market_indicator_service as target
    from app.services.market_indicator_service import MarketIndicatorService

    df = _load_reference_df("btcusdt_1d_tradingview_reference.csv")
    computed = _compute_fixture(MarketIndicatorService(), df, "BTCUSDT", "1d").head(1)
    computed.at[computed.index[0], "chart_patterns"] = [
        {
            "pattern": "golden_cross",
            "direction": "bullish",
            "confidence": 100,
            "ts": "2026-01-01T00:00:00Z",
            "reference_price": 100.0,
            "source": "chart_pattern_service",
            "dedupe_key": "golden_cross:1",
            "metadata": {"fast_ma": "sma_20", "slow_ma": "sma_50"},
        }
    ]

    class FakeConn:
        def __init__(self) -> None:
            self.statement = None
            self.params = None

        def execute(self, statement, params=None):
            self.statement = str(statement)
            self.params = params

    class FakeBegin:
        def __init__(self, conn: FakeConn) -> None:
            self.conn = conn

        def __enter__(self) -> FakeConn:
            return self.conn

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    class FakeEngine:
        def __init__(self) -> None:
            self.conn = FakeConn()

        def begin(self) -> FakeBegin:
            return FakeBegin(self.conn)

    fake_engine = FakeEngine()
    monkeypatch.setattr(target, "engine", fake_engine)

    MarketIndicatorService()._upsert_indicators(computed, is_recomputed=True)

    assert "ON CONFLICT (symbol, timeframe, ts)" in fake_engine.conn.statement
    assert "bb_upper_20_2 = EXCLUDED.bb_upper_20_2" in fake_engine.conn.statement
    assert "ichimoku_chikou_26 = EXCLUDED.ichimoku_chikou_26" in fake_engine.conn.statement
    assert "chart_patterns = EXCLUDED.chart_patterns" in fake_engine.conn.statement
    assert fake_engine.conn.params[0]["bb_upper_20_2"] is None
    assert fake_engine.conn.params[0]["atr_14"] is None
    assert fake_engine.conn.params[0]["ichimoku_tenkan_9"] is None
    assert fake_engine.conn.params[0]["obv"] == 42000.0
    assert '"pattern": "golden_cross"' in fake_engine.conn.params[0]["chart_patterns"]
    assert fake_engine.conn.params[0]["is_recomputed"] is True
