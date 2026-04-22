# Design: Multi-timeframe OHLCV Timescale Change

## Storage model

- Use one canonical table `market_ohlcv` with a `(symbol, timeframe, candle_time)` grain.
- Promote to Timescale hypertable with `candle_time` as time dimension.
- Use compressed chunks for historical data (older than 30 days), keeping hot data readable and indexable for recent windows.

## Ingestion flow

1. Scheduler ticks per timeframe.
2. For each `(symbol, timeframe)`:
   1. compute fetch window from latest persisted candle
   2. fetch from provider with overlap of one candle to avoid gaps
   3. normalize and upsert
3. emit metrics for lag and duplicate count.

## Read flow

1. API layer receives time window + symbol + timeframe.
2. Query persisted table with strict bounds (`limit`, `since/until`).
3. Return rows sorted descending or ascending depending on caller convention.
4. Only on cache miss and explicit fallback mode: query provider cache.

## Operational controls

- `TIMEFRAME_LIST` is explicit and validated: `1m, 5m, 1h, 4h, 1d`.
- Retention/Compression policies are enforced at DB level and monitored through health checks.
