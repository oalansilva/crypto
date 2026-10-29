# data-caching Specification

## Purpose
TBD - created by archiving change incremental-data-storage. Update Purpose after archive.
## Requirements
### Requirement: Incremental Data Storage

The system MUST keep a local Parquet read cache of OHLCV data for analysis performance, derived from the canonical history in PostgreSQL. The cache MUST NOT download candles from the exchange on its own: a missing period is first collected into the canonical history (only the missing part), then materialized into the cache. Each cache file MUST be identified by series and data version, and deleting it MUST NOT lose history.

#### Scenario: First Run (Download All)
- **WHEN** no cache exists for "BTC/USDT" on "1h" and the canonical history covers the requested period
- **THEN** the system MUST materialize the cache from PostgreSQL
- **AND** MUST NOT call the exchange

#### Scenario: Incremental Update (Delta Download)
- **WHEN** the canonical history ends at "2023-02-01 00:00:00" and a read asks up to "2023-03-01"
- **THEN** the system MUST collect only the missing part into the canonical history
- **AND** rebuild or extend the cache from the canonical history, under the series version

#### Scenario: Slice Retrieval (No Network)
- **WHEN** the cache for the current series version covers "2020-01-01" to "2024-01-01" and a read asks "2022-01-01" to "2022-02-01"
- **THEN** the system MUST return the slice from the Parquet cache
- **AND** MUST NOT make any network request to the exchange

#### Scenario: Stale version
- **WHEN** the series version changes after a correction
- **THEN** the cache of the previous version is not used for new reads

### Requirement: Cache Exchange Symbols
The System SHALL cache the list of available trading pairs (symbols) fetched from the exchange API (Binance) to minimize latency and API calls.
The cache MUST be persisted to disk (e.g., JSON or SQLite) and remain valid for a configurable duration (default: 24 hours).#### Scenario: First Fetch (Cache Miss)
Given the cache file does not exist or is older than 24 hours
When the System requests the list of symbols
Then it MUST fetch the latest markets from the Binance API
And filter the list to include ONLY pairs ending in "/USDT"
And save the filtered result to the local cache file
And return the list to the caller

#### Scenario: Subsequent Fetch (Cache Hit)
Given the cache file exists and is younger than 24 hours
When the System requests the list of symbols
Then it MUST read the list directly from the local cache file
And return the list immediately without calling the external API

### Requirement: Multi-Timeframe Data Storage
The system SHALL support fetching and caching multiple timeframes for the same symbol simultaneously.#### Scenario: Fetch both daily and hourly data
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

