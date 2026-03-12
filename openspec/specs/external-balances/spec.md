# external-balances Specification

## Purpose
TBD - created by archiving change external-balances-dashboard. Update Purpose after archive.
## Requirements
### Requirement: System MUST provide a Binance Spot balances snapshot endpoint
The system MUST provide a backend endpoint that returns the current Binance Spot balances using a configured read-only API key.

#### Scenario: Successful snapshot
- **WHEN** the user requests the Binance Spot snapshot
- **THEN** the system MUST return a JSON payload containing balances with `asset`, `free`, `locked`, and `total`

#### Scenario: Secret missing
- **WHEN** Binance credentials are not configured on the server
- **THEN** the system MUST return an error that clearly indicates missing configuration

### Requirement: System MUST provide a UI page to display external balances
The system MUST provide a UI page that displays Binance Spot balances in a readable list.

#### Scenario: Display balances
- **WHEN** the user opens the external balances page (`/external/balances`)
- **THEN** the UI MUST show the list of balances and highlight which assets have `locked` amounts

#### Scenario: Sorting
- **WHEN** balances are displayed
- **THEN** the UI MUST sort by `total` descending by default (largest balances first)

### Requirement: Integration MUST be read-only
The system MUST NOT place orders, withdraw, or modify the Binance account.

#### Scenario: Read-only enforcement
- **WHEN** the system is configured for Binance
- **THEN** it MUST only call read-only Binance endpoints

### Requirement: System MUST compute average buy cost for Binance Spot assets (USDT pairs)
The system MUST compute an average buy cost (USDT) per asset using Binance Spot executed trades for the symbol `ASSETUSDT`.

#### Scenario: Only USDT pairs are considered
- **WHEN** the system computes average cost for an asset
- **THEN** it MUST only use the `ASSETUSDT` symbol (no other quote currencies) in phase 1

#### Scenario: Buys-only cost basis
- **WHEN** trades exist for `ASSETUSDT`
- **THEN** the system MUST compute average buy cost using **buys only**
- **AND** it MUST ignore sells in phase 1

#### Scenario: No trades
- **WHEN** no executed trades are found for the symbol
- **THEN** average cost MUST be `null`

### Requirement: Wallet API MUST return PnL fields
The Wallet balances endpoint MUST return, for each balance row:
- `avg_cost_usdt` (nullable)
- `pnl_usd` (nullable)
- `pnl_pct` (nullable)

#### Scenario: PnL calculation
- **WHEN** `avg_cost_usdt` is available and current price is available
- **THEN** the system MUST compute:
  - `pnl_usd = (price_usdt - avg_cost_usdt) * total`
  - `pnl_pct = (price_usdt / avg_cost_usdt - 1) * 100`

### Requirement: Wallet UI MUST display PnL
The Wallet UI (`/external/balances`) MUST display PnL columns and visually indicate profit vs loss.

#### Scenario: Display
- **WHEN** the user opens the Wallet
- **THEN** it MUST show `avg_cost_usdt`, `pnl_usd`, and `pnl_pct` when available
- **AND** show `-` when not available

### Requirement: Wallet API MUST return snapshot timestamp
The Wallet balances endpoint MUST return an `as_of` timestamp so the UI can display when the snapshot was taken.

#### Scenario: Timestamp present
- **WHEN** the user calls `GET /api/external/binance/spot/balances`
- **THEN** the response MUST include `as_of`

### Requirement: Wallet API MUST support dust threshold override
The Wallet balances endpoint MUST accept a query param `min_usd` (optional float) to override dust filtering.

#### Scenario: Default dust behavior
- **WHEN** `min_usd` is not provided
- **THEN** the endpoint MUST behave with the default dust threshold (currently 0.02)

#### Scenario: Include dust
- **WHEN** `min_usd=0`
- **THEN** the endpoint MUST include rows that would otherwise be filtered as dust

### Requirement: Wallet UI MUST provide search and locked-only filtering

#### Scenario: Search
- **WHEN** the user searches by asset symbol
- **THEN** the UI MUST filter rows case-insensitively by `asset`

#### Scenario: Locked only
- **WHEN** the user enables a "locked only" filter
- **THEN** the UI MUST show only rows where `locked > 0`

### Requirement: Wallet UI MUST be usable on mobile
- **WHEN** the viewport is narrow
- **THEN** the UI MUST not require horizontal scrolling to inspect balances

