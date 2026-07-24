## ADDED Requirements

### Requirement: Dedicated continuous candle writer per environment
Each operational environment (DEV and PROD) SHALL run exactly one dedicated canonical candle writer timer that periodically updates `market_ohlcv` for configured symbols and timeframes, without enabling candle writing inside the API process.

#### Scenario: DEV restart preserves periodic writer
- **WHEN** an operator runs the canonical DEV `./restart`
- **THEN** the DEV candle writer timer SHALL be installed or left enabled
- **AND** the API process SHALL keep candle writer / in-process OHLCV ingestion disabled

#### Scenario: writer mutual exclusion
- **WHEN** a candle writer process already holds the writer lock
- **AND** another writer invocation starts
- **THEN** the second invocation SHALL skip without fetching exchange candles
- **AND** it SHALL record a skipped-lock state

#### Scenario: configurable load bounds
- **WHEN** the writer runs
- **THEN** it SHALL ingest only symbols and timeframes allowed by environment configuration
- **AND** it SHALL use incremental fetches from the latest persisted candle with a bounded overlap

### Requirement: Degraded candle API signaling
When canonical candle mode is enabled and persisted candles are older than the freshness tolerance for the requested timeframe, the market candles API SHALL NOT present them as fresh canonical data.

#### Scenario: stale persisted candles are marked degraded
- **WHEN** a client requests `/api/market/candles` in canonical mode
- **AND** persisted candles exist but exceed the timeframe freshness tolerance
- **AND** direct Binance fetch fallback is disabled
- **THEN** the response SHALL include the persisted candles
- **AND** it SHALL mark the payload as degraded/stale with lag information

#### Scenario: direct fallback remains explicit contingency
- **WHEN** direct Binance fetch fallback is explicitly enabled
- **AND** persisted candles are stale
- **THEN** the API MAY fetch candles from Binance as contingency
- **AND** that path SHALL remain opt-in via configuration

### Requirement: Lag metric and alert observability
The system SHALL expose candle lag observability for configured symbol/timeframe pairs and SHALL emit an alert signal when lag exceeds the configured tolerance.

#### Scenario: lag exceeds tolerance during writer run
- **WHEN** the writer finishes ingesting a symbol/timeframe
- **AND** the latest candle lag exceeds the configured threshold
- **THEN** the system SHALL record an alertable lag event for that symbol and timeframe

#### Scenario: operators can inspect freshness evidence
- **WHEN** an operator inspects runtime status or candle metrics
- **THEN** the response SHALL include candle writer enablement, lock/latest-run state, and lag-related metrics without exposing secrets
