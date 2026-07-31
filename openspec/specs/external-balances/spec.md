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
The system MUST compute a reference buy cost (USD-stable) per asset using Binance Spot executed buy trades for that asset.

For each non-stable asset in the wallet snapshot, the system MUST consider executed trades from supported USD-stable quote pairs, at least `ASSETUSDT` and `ASSETUSDC`. The wallet response field MAY remain named `avg_cost_usdt` for compatibility.

#### Scenario: Supported stable quotes are considered for every asset
- **WHEN** the system computes average/reference buy cost for any asset in the wallet snapshot
- **THEN** it MUST query supported quote pairs including `ASSETUSDT` and `ASSETUSDC`
- **AND** it MUST NOT hardcode a single asset symbol (rule applies to all balances)

#### Scenario: Latest buy across supported quotes wins
- **WHEN** buy trades exist in one or more supported quote pairs
- **THEN** the system MUST use the most recent buy trade price among those pairs as the reference cost
- **AND** it MUST ignore sells

#### Scenario: USDC buy is preferred over older USDT buy
- **WHEN** an asset has a newer buy on `ASSETUSDC` and an older buy on `ASSETUSDT`
- **THEN** the reference cost MUST come from the newer `ASSETUSDC` buy

#### Scenario: USDT-only assets remain correct
- **WHEN** buy trades exist only on `ASSETUSDT`
- **THEN** the reference cost MUST continue to use that latest USDT buy

#### Scenario: No trades
- **WHEN** no executed buy trades are found on any supported quote pair
- **THEN** average/reference cost MUST be `null`

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
The Wallet UI SHALL render correctly on narrow viewports without horizontal scrolling.

#### Scenario: Mobile balance inspection
- **WHEN** the user opens the Wallet on a mobile device (viewport < 768px)
- **THEN** the UI MUST not require horizontal scrolling to inspect balances
- **AND** the balance list SHALL adapt to a single-column layout

### Requirement: Wallet UI MUST use the Crypto Workbench layout
The Wallet UI (`/external/balances`) MUST present account balances in a compact operational layout aligned with the supplied Crypto Workbench template.

#### Scenario: Wallet overview
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show the page title, Binance read-only context, last synchronization time when available, total wallet value, visible asset count, partial PnL summary, and performance summary

#### Scenario: Credential panel
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show whether Binance credentials are configured (optionally with masked API key) and a clear action/link to manage them in Meu Perfil (`/profile`), without being the primary full Key/Secret editor

#### Scenario: Filter toolbar
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show search, dust threshold, sort selection, reset filters, and export CSV controls in one compact toolbar

#### Scenario: Desktop balance table
- **WHEN** balances are displayed on a desktop viewport
- **THEN** the UI MUST show a tabular balance list with asset, total, free, value USD, price, average cost, PnL, and allocation share

#### Scenario: Mobile balance cards
- **WHEN** balances are displayed on a narrow viewport
- **THEN** the UI MUST show a single-column card list without requiring horizontal scrolling

### Requirement: Wallet shows credential status and links to user profile
The external balances (Carteira) page MUST NOT be the primary place to edit Binance API Key/Secret. It MUST show whether credentials are configured and direct the user to `/profile` to manage them.

#### Scenario: Credentials not configured on wallet
- **WHEN** the user opens `/external/balances` without Binance credentials
- **THEN** the page MUST show status `Não configurada` and a clear action/link to configure credentials in Meu Perfil

#### Scenario: Credentials configured on wallet
- **WHEN** the user opens `/external/balances` with Binance credentials configured
- **THEN** the page MUST show status `Configurada` (optionally with masked API Key) and still allow navigating to Meu Perfil to change or remove them

#### Scenario: Wallet continues using per-user credentials
- **WHEN** the user has credentials saved in Meu Perfil
- **THEN** the wallet balances snapshot MUST continue to use the logged-in user's Binance credentials without requiring re-entry on the wallet page

### Requirement: Wallet PnL uses the multi-quote reference buy cost
PnL fields MUST be computed from the multi-quote reference buy cost and the current spot price already used by the wallet snapshot.

#### Scenario: PnL follows corrected cost
- **WHEN** reference cost comes from a USDC buy and current price is available
- **THEN** the system MUST compute:
  - `pnl_usd = (price_usdt - avg_cost_usdt) * total`
  - `pnl_pct = (price_usdt / avg_cost_usdt - 1) * 100`
