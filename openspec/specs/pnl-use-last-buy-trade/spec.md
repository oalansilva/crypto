# pnl-use-last-buy-trade Specification

## Purpose
TBD - created by archiving change pnl-use-last-buy-trade. Update Purpose after archive.
## Requirements
### Requirement: PnL must use the latest buy trade as purchase reference on external balances
The `/external/balances` flow MUST derive each asset purchase reference from the most recent buy trade for that asset instead of averaging historical buys.

#### Scenario: Multiple buy trades for the same asset
- **GIVEN** an asset has more than one historical buy trade
- **WHEN** `/external/balances` computes the purchase reference and unrealized PnL for that asset
- **THEN** it MUST use only the latest buy trade price for that asset
- **AND** it MUST NOT average older buy trades into that purchase reference

#### Scenario: Asset without buy trades
- **GIVEN** an asset has no buy trade history
- **WHEN** `/external/balances` computes the purchase reference and unrealized PnL
- **THEN** it MUST keep the existing safe fallback behavior for assets without buy trades

