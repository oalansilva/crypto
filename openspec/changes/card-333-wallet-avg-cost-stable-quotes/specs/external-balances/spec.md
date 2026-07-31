## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Wallet PnL uses the multi-quote reference buy cost
PnL fields MUST be computed from the multi-quote reference buy cost and the current spot price already used by the wallet snapshot.

#### Scenario: PnL follows corrected cost
- **WHEN** reference cost comes from a USDC buy and current price is available
- **THEN** the system MUST compute:
  - `pnl_usd = (price_usdt - avg_cost_usdt) * total`
  - `pnl_pct = (price_usdt / avg_cost_usdt - 1) * 100`
