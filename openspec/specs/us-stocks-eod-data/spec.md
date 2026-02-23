# us-stocks-eod-data Specification

## Purpose
TBD - created by archiving change us-stocks-eod-stooq-provider. Update Purpose after archive.
## Requirements
### Requirement: Fetch US stock/ETF EOD candles via Stooq
The system MUST be able to fetch end-of-day (1D) OHLCV candle data for US stocks and ETFs using Stooq as a free data source.

#### Scenario: Fetch EOD candles for a US ticker
- **WHEN** a backtest or monitor requests OHLCV for `AAPL` with timeframe `1d` and source `stooq`
- **THEN** the system returns a normalized OHLCV dataframe/array with columns: time, open, high, low, close, volume

### Requirement: Normalize provider-specific symbols for US stocks
The system MUST support mapping user-facing US tickers (e.g., `AAPL`, `SPY`) to Stooq provider symbols (e.g., `aapl.us`, `spy.us`).

#### Scenario: Symbol mapping for Stooq
- **WHEN** the user requests symbol `SPY` for source `stooq`
- **THEN** the system maps it to `spy.us` for the provider request

### Requirement: Cache EOD responses to minimize load
The system MUST cache fetched EOD results for a symbol/timeframe/source and avoid refetching within the cache TTL.

#### Scenario: Cached EOD request
- **WHEN** two requests for `AAPL` timeframe `1d` source `stooq` happen within the cache TTL
- **THEN** the second request is served from cache without an external provider fetch

### Requirement: EOD-only constraint enforcement
The system MUST enforce that the Stooq provider is used only for EOD (1D) timeframes unless explicitly supported.

#### Scenario: Reject unsupported intraday timeframe
- **WHEN** the user requests timeframe `1h` using source `stooq`
- **THEN** the system returns a validation error indicating the provider supports EOD (1D) only

