## ADDED Requirements

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
