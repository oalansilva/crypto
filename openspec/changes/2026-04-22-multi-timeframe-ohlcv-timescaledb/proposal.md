# Persist OHLCV candles in TimescaleDB across multi-timeframes

## Why

The system currently serves candles mostly from in-memory caches and provider adapters, with no durable, query-optimized persistence for historical OHLCV at the application layer. This blocks efficient historical analysis and makes large-window monitoring/backtesting behavior depend on external latency.

## What Changes

- Introduce a durable OHLCV storage model in PostgreSQL/TimescaleDB.
- Add a dedicated ingestion path to continuously persist candles for the required timeframes: `1m`, `5m`, `1h`, `4h`, `1d`.
- Configure the table as a Timescale hypertable and tune it for retention and compression:
  - retention of at least 2 years of historical candles
  - automatic compression after 30 days
- Provide query patterns and indexes that satisfy low-latency reads for market chart and monitor endpoints.

## What This Change Does Not Do

- It does not add a new UI for historical candle exploration; it prepares the backend persistence and query path only.
- It does not replace upstream providers; it persists data from the existing market data providers and can continue using provider fallback logic.

## Capabilities

### New Capabilities
- `ohlcv-timescale-raw-hypertable`: persist normalized candles into a Timescale hypertable keyed by symbol/timeframe/timestamp.
- `continuous-candle-ingestion`: schedule back-to-live ingestion jobs for all required timeframes.
- `ohlcv-retention-policy`: enforce retention window >= 2 years in the database.
- `ohlcv-compression-policy`: compress chunks automatically after 30 days.
- `ohlcv-low-latency-query-path`: provide indexed, bounded queries for chart/monitor screens with response targets under 500ms.

### Modified Capabilities
- `market-candles-api`: consume persisted candles as the primary source for `GET /api/market/candles`.
- `incremental-loader`: shift from file-cache-first behavior toward DB-backed storage for shared historical calls.

## Impact

- Backend: new DB migration and service modules for candle persistence, compression/retention policy management, and query optimization.
- Data quality: deduplication strategy required for overlapping fetch windows to avoid duplicates by `(symbol, timeframe, timestamp)`.
- Operational: additional background scheduler load; add monitoring for ingestion lag and failed writes.
- Security: existing DB role boundaries and least-privilege access patterns apply to new tables and jobs.
