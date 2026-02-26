## Why

The Wallet (Carteira) currently shows spot balances and USD valuation, but it does not show whether a position is profitable. We want to show per-asset PnL based on the user's average buy cost.

## What Changes

- Add backend support to compute an **average buy price** for Binance Spot assets using Binance Spot **executed trades** (myTrades) for **USDT pairs only**.
- Add PnL fields to the Wallet UI for each asset:
  - avg_cost_usdt
  - pnl_usd
  - pnl_pct
- Keep the initial cost basis model simple:
  - Average cost is computed from **buys only**.
  - Sells are **ignored** in phase 1.

## Capabilities

### New Capabilities
- `wallet-pnl-binance`: Compute and display Binance Spot PnL based on average buy cost from executed trades.

### Modified Capabilities
- `external-balances`: Wallet page will show PnL columns.

## Impact

- Backend: new endpoint(s) to retrieve executed trades for relevant symbols and compute avg cost.
- Frontend: display PnL columns and status (profit/loss).
- Ops: requires Binance read-only API key with permission to read account trades.
