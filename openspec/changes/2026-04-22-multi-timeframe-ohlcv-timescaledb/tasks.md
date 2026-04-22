# Tasks: Multi-timeframe OHLCV Timescale Storage

## 1) Database and migration baseline

- [x] 1.1 Add migration to create `market_ohlcv` table with canonical columns:
  - `symbol text`
  - `timeframe text`
  - `candle_time timestamptz`
  - `open numeric`, `high numeric`, `low numeric`, `close numeric`
  - `volume numeric`, `source text`, `created_at timestamptz`
- [x] 1.2 Add unique constraint/index for `(symbol, timeframe, candle_time, source)` and idempotent upsert support.
- [x] 1.3 Convert table to hypertable on `candle_time`.
- [x] 1.4 Create indexes for query patterns:
  - `(symbol, timeframe, candle_time DESC)`
  - optional BRIN or compression-order indexes after benchmark.

## 2) Retention and compression policies

- [x] 2.1 Enable Timescale retention policy for at least 2 years.
- [x] 2.2 Enable compression policy:
  - compress after 30 days
  - segment-by segment compression policy tuned for this table
- [ ] 2.3 Add operational command or startup verification that policies are active in non-local environments.

## 3) Ingestion service

- [x] 3.1 Add backend service `CandleIngestionService` with per-timeframe scheduler jobs.
- [x] 3.2 Add supported timeframe map to include `1m` and `5m` with existing `1h`, `4h`, `1d`.
- [x] 3.3 Implement dedupe-aware write path:
  - detect and merge overlapping bars
  - use upsert for exact `(symbol, timeframe, candle_time)` conflicts.
- [x] 3.4 Add backfill + catch-up strategy per symbol/timeframe.

## 4) Query/read path update

- [x] 4.1 Update `GET /api/market/candles` (or new endpoint variant) to read from Timescale first.
- [x] 4.2 Enforce bounded limits by default to keep read latency under 500ms.
- [x] 4.3 Add optional fallback to provider cache only when DB empty/temporarily inconsistent.
- [ ] 4.4 Add index usage assertions in code (and optional `EXPLAIN` checks in tests) to avoid accidental full scans.

## 5) Observability and correctness

- [ ] 5.1 Add metrics for insert lag, duplicates skipped, and query latency p50/p95/p99.
- [ ] 5.2 Add alerts for ingestion delay > configured threshold per timeframe.
- [ ] 5.3 Add structured logs for retention/compression policy failures.

## 6) Validation

- [ ] 6.1 Add integration tests:
  - `INSERT -> UPSERT -> query` for duplicate prevention
  - compression policy enablement
  - retention policy effect with synthetic old rows
  - 1m/5m support and query-time filtering by timeframe
- [ ] 6.2 Add performance test for a realistic read scenario with `limit` and window filters to validate < 500ms in CI or staging profile.
