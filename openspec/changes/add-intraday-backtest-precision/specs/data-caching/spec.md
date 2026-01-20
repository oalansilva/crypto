## ADDED Requirements

### Requirement: Multi-Timeframe Data Storage
The system SHALL support fetching and caching multiple timeframes for the same symbol simultaneously.

#### Scenario: Fetch both daily and hourly data
- **WHEN** a backtest requests precise mode for BTC/USDT
- **THEN** the system fetches and caches both 1d and 1h data
- **AND** stores them in separate Parquet files (`BTC_USDT_1d.parquet`, `BTC_USDT_1h.parquet`)

#### Scenario: Validate intraday cache freshness
- **WHEN** intraday data is requested
- **THEN** the system checks if cached 1h data covers the requested date range
- **AND** fetches missing data from the exchange API if needed

### Requirement: Intraday Data Availability Check
The system SHALL provide an endpoint to check intraday data coverage before running precise backtests.

#### Scenario: Check 1h data availability
- **WHEN** user requests `/api/data/intraday-availability?symbol=BTC/USDT&timeframe=1h&since=2020-01-01`
- **THEN** return `{ "available": true, "coverage": { "start": "2020-01-01", "end": "2025-10-15" } }`
- **OR** return `{ "available": false, "reason": "Insufficient data before 2021-01-01" }`
