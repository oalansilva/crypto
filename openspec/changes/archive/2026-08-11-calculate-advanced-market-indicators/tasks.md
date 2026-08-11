## 1. Schema And Storage

- [x] 1.1 Add PostgreSQL migration fields or equivalent storage for Bollinger, ATR, Stochastic, OBV, and Ichimoku values.
- [x] 1.2 Update startup schema guard for `market_indicator` so fresh environments include advanced indicator storage.
- [x] 1.3 Preserve unique `(symbol, timeframe, ts)` writes and nullable warmup values for all advanced fields.
- [x] 1.4 Update latest/time-series read queries to return advanced indicator fields with existing metadata.

## 2. Calculation Pipeline

- [x] 2.1 Extend `MarketIndicatorService._compute_indicators` to calculate Bollinger Bands with length 20 and 2 standard deviations.
- [x] 2.2 Add ATR 14 calculation using the selected runtime engine and documented smoothing semantics.
- [x] 2.3 Add Stochastic 14/3/3 calculation with `%K` and `%D` outputs.
- [x] 2.4 Add OBV calculation from close and volume.
- [x] 2.5 Add Ichimoku calculation using highest-high/lowest-low midpoint formulas and documented displacement metadata.
- [x] 2.6 Update upsert serialization so all advanced values persist idempotently during full and incremental recompute.

## 3. Documentation And Formula Evidence

- [x] 3.1 Document formulas, defaults, warmup behavior, and displacement semantics in the change handoff or market-indicators docs.
- [x] 3.2 Record the validation sources for each indicator: TradingView fixture input, TA-Lib where applicable, pandas-ta where applicable, and independent formula implementation.
- [x] 3.3 Document why Ichimoku uses custom formula validation instead of TA-Lib parity.

## 4. Validation Tests

- [x] 4.1 Use existing TradingView fixture CSVs as reference OHLCV inputs and preserve existing TradingView basic-indicator parity.
- [x] 4.2 Add TA-Lib and pandas-ta parity checks for Bollinger, ATR, Stochastic, and OBV with indicator-specific tolerances.
- [x] 4.3 Add independent formula parity checks for all advanced indicators, including Ichimoku.
- [x] 4.4 Add tests proving warmup nulls and incremental recompute remain idempotent for advanced fields.
- [x] 4.5 Run targeted unit tests for market indicator fixtures and recompute behavior.

## 5. Scoring And Operational Readiness

- [x] 5.1 Confirm scoring reads advanced indicators from dedicated storage and does not recalculate them inline.
- [x] 5.2 Add a controlled recompute/backfill note for existing symbols and timeframes.
- [x] 5.3 Reconcile `tasks.md`, implementation evidence, and handoff before moving the change to QA.

## 6. Project Skills Reminder

- [x] 6.1 Use relevant project skills when applying this change, especially architecture review, db migration review, unit test planning, debugging checklist, and CI failure triage if needed.
