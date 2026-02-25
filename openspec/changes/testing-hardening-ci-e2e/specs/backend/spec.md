## ADDED Requirements

### Requirement: Backtest endpoint selects correct data source for US tickers
The backend MUST select the correct market data source for US tickers when running combo backtests.

#### Scenario: US ticker uses stooq by default
- **WHEN** the client requests a combo backtest for a symbol without "/" (e.g., "NVDA")
- **THEN** the backend uses the stooq provider unless an explicit data source is provided

#### Scenario: Explicit parameter data_source overrides default
- **WHEN** the client provides `parameters.data_source` or `request.data_source`
- **THEN** the backend uses the requested data source (if supported for the timeframe)

### Requirement: Batch backtest selects correct data source per symbol
The backend MUST infer a per-symbol data source for batch backtests when the request omits `data_source`.

#### Scenario: Batch infers per symbol
- **WHEN** a batch backtest request omits `data_source`
- **THEN** the backend infers stooq for symbols without "/" and ccxt for symbols with "/"

### Requirement: Opportunities endpoint remains responsive
The backend MUST keep the opportunities endpoint responsive under normal conditions.

#### Scenario: Opportunities responds under target duration
- **WHEN** `GET /api/opportunities/?tier=all` is requested
- **THEN** the endpoint responds successfully within a configurable target duration in automated smoke tests
