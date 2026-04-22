# ohlcv-storage Specification

## Purpose
TBD - created by archiving change 2026-04-22-multi-timeframe-ohlcv-timescaledb. Update Purpose after archive.
## Requirements
### Requirement: Persist OHLCV candles in a Timescale hypertable
The system SHALL persist normalized OHLCV candles in a dedicated Timescale hypertable table.

#### Scenario: Candle write
- **WHEN** a new candle is successfully fetched from a provider
- **THEN** the system SHALL upsert it into `market_ohlcv`
- **AND** deduplicate by `(symbol, timeframe, candle_time)` to avoid duplicates caused by overlaps.

#### Scenario: Timeframe coverage
- **WHEN** a candle read/write request occurs
- **THEN** the timeframes supported by persistence SHALL include `1m`, `5m`, `1h`, `4h`, `1d`.

### Requirement: Continuous ingestion
The system SHALL keep candle history updated continuously for configured symbols and supported timeframes.

#### Scenario: Incremental updates
- **WHEN** scheduler window advances
- **THEN** the system SHALL fetch only missing/updatable bars for each symbol/timeframe
- **AND** persist without backfilling all historical rows each run.

### Requirement: Data retention
The system SHALL keep at least 2 years of raw candles in Timescale partitions.

#### Scenario: Retention policy
- **WHEN** retention policy is evaluated
- **THEN** rows older than 2 years ARE dropped for each candle table/chunk.

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

