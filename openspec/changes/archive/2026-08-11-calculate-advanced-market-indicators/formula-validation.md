## Formula Documentation

This change extends the dedicated `market_indicator` pipeline with source-candle-aligned
advanced indicator fields. Warmup values remain null until each rolling window has enough
history.

### Bollinger Bands

- Columns: `bb_upper_20_2`, `bb_middle_20_2`, `bb_lower_20_2`
- Defaults: length 20, standard deviation multiplier 2, SMA middle band
- Formula:
  - `middle = SMA(close, 20)`
  - `upper = middle + 2 * STDDEV(close, 20)`
  - `lower = middle - 2 * STDDEV(close, 20)`
- Validation sources:
  - TradingView OHLCV fixture data used as the input candle source.
  - TA-Lib `BBANDS`.
  - pandas-ta `bbands`.
  - Independent pandas rolling SMA/stddev formula in tests.

### ATR

- Column: `atr_14`
- Defaults: length 14
- Formula:
  - `TR = max(high - low, abs(high - previous_close), abs(low - previous_close))`
  - Runtime uses TA-Lib ATR/Wilder smoothing.
- Validation sources:
  - TradingView OHLCV fixture data used as the input candle source.
  - TA-Lib `ATR`.
  - pandas-ta `atr`.
  - Independent True Range/Wilder smoothing formula in tests.

### Stochastic

- Columns: `stoch_k_14_3_3`, `stoch_d_14_3_3`
- Defaults: fast `%K` length 14, `%K` smoothing 3, `%D` smoothing 3
- Formula:
  - `fast_k = (close - lowest_low_14) / (highest_high_14 - lowest_low_14) * 100`
  - `stoch_k = SMA(fast_k, 3)`
  - `stoch_d = SMA(stoch_k, 3)`
- Validation sources:
  - TradingView OHLCV fixture data used as the input candle source.
  - TA-Lib `STOCH`.
  - pandas-ta `stoch`.
  - Independent rolling high/low and SMA formula in tests.

### OBV

- Column: `obv`
- Defaults: close and volume input, no lookback period
- Formula:
  - If current close is above previous close, add current volume.
  - If current close is below previous close, subtract current volume.
  - If current close is equal to previous close, keep previous OBV.
- Validation sources:
  - TradingView OHLCV fixture data used as the input candle source.
  - TA-Lib `OBV`.
  - pandas-ta `obv`.
  - Independent cumulative close-direction formula in tests.

### Ichimoku

- Columns:
  - `ichimoku_tenkan_9`
  - `ichimoku_kijun_26`
  - `ichimoku_senkou_a_9_26_52`
  - `ichimoku_senkou_b_9_26_52`
  - `ichimoku_chikou_26`
- Defaults: Tenkan 9, Kijun 26, Senkou Span B 52, displacement 26
- Formula:
  - `tenkan = (highest_high_9 + lowest_low_9) / 2`
  - `kijun = (highest_high_26 + lowest_low_26) / 2`
  - `senkou_a = (tenkan + kijun) / 2`
  - `senkou_b = (highest_high_52 + lowest_low_52) / 2`
  - `chikou = close`
- Storage semantics:
  - Values are stored aligned to the source candle timestamp.
  - Displacement is recorded in `source_window.advanced_indicators.ichimoku.displacement`.
  - The pipeline does not write projected future rows or past rows for shifted chart display.
- Validation sources:
  - TradingView OHLCV fixture data used as the input candle source.
  - TA-Lib is not applicable because TA-Lib does not provide an Ichimoku function.
  - pandas-ta is used only as a secondary review source for Tenkan/Kijun naming and
    displacement behavior, not as strict parity for persisted source-aligned spans.
  - Independent rolling highest-high/lowest-low formula in tests.

## Backfill / Recompute Note

Existing rows will have null advanced fields until recomputed. Use the existing admin
indicator recompute endpoint with `forceFull=true` for a controlled full backfill by
symbol/timeframe, or the default incremental recompute for routine updates:

```json
{
  "symbol": "BTCUSDT",
  "timeframes": ["1h", "1d"],
  "forceFull": true
}
```

Backfill should be run in small batches per symbol to keep PostgreSQL write pressure
predictable.
