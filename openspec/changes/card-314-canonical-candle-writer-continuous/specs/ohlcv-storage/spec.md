## MODIFIED Requirements

### Requirement: Continuous ingestion
The system SHALL keep candle history updated continuously for configured symbols and supported timeframes through the dedicated canonical candle writer, not through the default API process.

#### Scenario: Incremental updates
- **WHEN** the dedicated candle writer window advances
- **THEN** the system SHALL fetch only missing/updatable bars for each configured symbol/timeframe
- **AND** persist without backfilling all historical rows each run
- **AND** the API process SHALL NOT start in-process OHLCV ingestion by default
