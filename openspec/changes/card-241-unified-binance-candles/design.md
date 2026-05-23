## Context

The canonical candle table already exists as `market_ohlcv`, but runtime behavior does not enforce it as the single source. Several flows call Binance/CCXT independently.

## Goals / Non-Goals

**Goals:**

- Establish `market_ohlcv` as the default read source for Binance OHLCV candles.
- Make direct Binance candle fetch explicit and centralized behind an ingestion/backfill path.
- Prevent backend/API boot from starting ingestion/backfill loops unless flags opt in.
- Keep the current application usable when canonical storage is unavailable by allowing an explicit legacy fallback flag.

**Non-Goals:**

- Rebuild every backtest and signal path in one pass.
- Remove price/ticker realtime snapshot behavior.
- Change strategy calculations.

## Decisions

- Add `CRYPTO_CANDLES_CANONICAL_MODE`, default `1`, as the service boundary. In canonical mode, read paths prefer `market_ohlcv` and do not direct-fetch Binance unless `CRYPTO_CANDLES_DIRECT_FETCH_FALLBACK=1`.
- Add `CRYPTO_CANDLES_WRITER_ENABLED`, default `0`, to identify the single process allowed to fetch/persist candles.
- Add `CRYPTO_CANDLES_INCREMENTAL_OVERLAP_CANDLES`, default `1`, for idempotent writer overlap. When a symbol/timeframe has no stored candles, the existing first-run lookback is used; after that the writer fetches from `latest_candle - one candle` through the current moment and upserts into `market_ohlcv`.
- Set the default writer/backfill timeframe scope to `15m,1d`. Other supported timeframes remain explicit opt-ins through `MARKET_OHLCV_TIMEFRAMES`, `BACKFILL_DEFAULT_TIMEFRAMES`, or `BACKFILL_SCHEDULER_TIMEFRAMES`.
- Set the default writer/backfill symbol scope to all Binance spot `*/USDT` pairs, filtered by the existing excluded-symbol rules. `MARKET_OHLCV_SYMBOLS` can still limit to an explicit comma-separated list; `MARKET_OHLCV_SYMBOL_LIMIT` can cap broad runs during probes.
- Expose a one-shot canonical writer command for controlled catch-up runs without starting the full background stack.
- Keep `MARKET_OHLCV_INGESTION_ENABLED` and `BACKFILL_SCHEDULER_ENABLED` default-off at runtime startup.
- Change `runtime_worker` startup to require `CRYPTO_RUNTIME_WORKER_ENABLED=1` plus at least one explicit `RUN_*` routine flag. This keeps older `.env` routine flags from starting the worker accidentally.
- Keep `crypto-stack` capable of starting everything, but only when flags are explicitly set.

## Risks / Trade-offs

- Some chart/API calls can return fewer candles until the canonical store is populated. This is intentional; explicit writer/backfill mode owns freshness.
- Legacy direct-fetch fallback remains available as an escape hatch while consumers are migrated.
