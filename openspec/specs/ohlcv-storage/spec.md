# ohlcv-storage Specification

## Purpose
TBD - created by archiving change 2026-04-22-multi-timeframe-ohlcv-timescaledb. Update Purpose after archive.
## Requirements
### Requirement: Persist OHLCV candles in a Timescale hypertable
The system SHALL persist normalized OHLCV candles in a dedicated Timescale hypertable table, keyed by series identity (asset, source, session, adjustment and timeframe) and candle time.

#### Scenario: Candle write
- **WHEN** a new candle is successfully fetched from a provider
- **THEN** the system SHALL upsert it into `market_ohlcv`
- **AND** deduplicate by `(series_id, candle_time)` to avoid duplicates caused by overlaps
- **AND** candles of different series (for example adjusted and unadjusted NVDA 1d) SHALL NOT overwrite each other.

#### Scenario: Timeframe coverage
- **WHEN** a candle read/write request occurs
- **THEN** the timeframes supported by persistence SHALL include `1m`, `5m`, `15m`, `1h`, `4h`, `1d`
- **AND** the 15m of stocks and ETFs SHALL be derived from 5m on read and SHALL NOT be stored as a native series.

### Requirement: Continuous ingestion
The system SHALL keep candle history updated continuously for configured symbols and supported timeframes.

#### Scenario: Incremental updates
- **WHEN** scheduler window advances
- **THEN** the system SHALL fetch only missing/updatable bars for each symbol/timeframe
- **AND** persist without backfilling all historical rows each run.

### Requirement: Data retention
The system SHALL keep stored candles as the canonical history. No time-based retention policy SHALL drop rows from `market_ohlcv`; removal happens only by an explicit, logged operation on a whole series.

#### Scenario: Retention policy
- **WHEN** the Timescale jobs for `market_ohlcv` are evaluated
- **THEN** there is no retention job dropping chunks by age
- **AND** candles older than 2 years remain queryable, compressed after 30 days.

### Requirement: Compression policy
The system SHALL compress chunks once data exceeds 30 days of age.

#### Scenario: Compression
- **WHEN** a chunk reaches 30 days old
- **THEN** it SHALL be eligible for Timescale compression
- **AND** compressed chunks SHALL remain queryable through standard candle fetch APIs.

### Requirement: Query performance target
The system SHALL return market candle queries within 500ms for normal dashboard windows.

#### Scenario: Bounded fetch
- **WHEN** clients request candles for chart/monitor rendering
- **THEN** the query SHALL enforce a sane default and maximum window/limit
- **AND** use indexed access paths on `(symbol, timeframe, candle_time DESC)`.

