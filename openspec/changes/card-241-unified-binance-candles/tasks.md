## 1. Runtime Boundaries

- [x] 1.1 Add canonical candle service configuration helpers.
- [x] 1.2 Disable backend OHLCV ingestion/backfill by default.
- [x] 1.3 Disable runtime worker routines by default.
- [x] 1.4 Make `start.sh` safe by default for Binance candle workers.
- [x] 1.5 Make the canonical writer incremental after first population.
- [x] 1.6 Add a one-shot canonical writer command for controlled catch-up.

## 2. Candle Consumers

- [x] 2.1 Route `/api/market/candles` through canonical reads before any direct provider fetch.
- [x] 2.2 Allow direct Binance fetch only through explicit fallback or writer mode.
- [x] 2.3 Preserve full-history/backfill scheduling semantics without immediate direct fetch loops.

## 3. Validation

- [x] 3.1 Add focused tests for canonical/default-off behavior.
- [x] 3.2 Run focused backend tests.
- [x] 3.3 Validate OpenSpec change.
