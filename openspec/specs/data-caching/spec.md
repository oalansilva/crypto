# data-caching Specification

## Purpose
TBD - created by archiving change incremental-data-storage. Update Purpose after archive.
## Requirements
### Requirement: Incremental Data Storage

The system MUST store OHLCV data locally in Parquet format to ensure high performance and avoid redundant downloads.
When specific time ranges are requested, the system MUST check local storage first.
If local data exists, it MUST determine the latest timestamp stored and ONLY download data from that point forward (incremental update).
New data MUST be appended to the local storage (Parquet file), ensuring the dataset grows over time without gaps.

#### Scenario: First Run (Download All)
Given that no local data exists for "BTC/USDT" on "1h" timeframe
When `fetch_data` is called for a period (e.g., 2023-01 to 2023-02)
Then the system MUST download data from the earliest available point or the start of the requested period
And save it to `data/storage/exchange/symbol/timeframe.parquet`

#### Scenario: Incremental Update (Delta Download)
Given that local data exists up to "2023-02-01 00:00:00"
When `fetch_data` is called with a range ending in "2023-03-01"
Then the system MUST read the keys/metadata from the local Parquet file
And determine the last timestamp is "2023-02-01"
And download ONLY the data from "2023-02-01" to "2023-03-01" (plus/minus 1 candle logic)
And append this new data to the Parquet file

#### Scenario: Slice Retrieval (No Network)
Given that local data exists from "2020-01-01" to "2024-01-01"
When `fetch_data` is called for "2022-01-01" to "2022-02-01"
Then the system MUST load the data from the Parquet file
And return the DataFrame sliced to the requested period
And MUST NOT make any network requests to the exchange

### Requirement: Cache Exchange Symbols
The System SHALL cache the list of available trading pairs (symbols) fetched from the exchange API (Binance) to minimize latency and API calls.
The cache MUST be persisted to disk (e.g., JSON or SQLite) and remain valid for a configurable duration (default: 24 hours).

#### Scenario: First Fetch (Cache Miss)
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

