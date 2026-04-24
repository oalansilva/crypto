## 1. OpenSpec And Contract

- [x] 1.1 Create proposal, design, and spec for dynamic support/resistance pivot levels.
- [x] 1.2 Define classic pivot formulas and persisted field names.

## 2. Storage And Read Path

- [x] 2.1 Add nullable numeric storage for `pivot_point`, S1-S3, and R1-R3 in `market_indicator`.
- [x] 2.2 Add Alembic migration and startup schema guard.
- [x] 2.3 Include pivot support/resistance fields in latest/time-series read queries.
- [x] 2.4 Serialize pivot support/resistance fields during indicator upsert.

## 3. Calculation Pipeline

- [x] 3.1 Implement classic pivot point calculation from previous candle OHLC.
- [x] 3.2 Preserve null warmup values for rows without previous candle context.
- [x] 3.3 Integrate calculation into `MarketIndicatorService._compute_indicators` for every processed timeframe.
- [x] 3.4 Document pivot formula metadata in `source_window`.

## 4. Validation

- [x] 4.1 Add unit tests for classic pivot formulas and warmup nulls.
- [x] 4.2 Add tests for market indicator upsert/read shape.
- [x] 4.3 Run targeted backend tests for market indicators.
