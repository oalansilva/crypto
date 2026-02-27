## Context

We already have a Wallet page that fetches Binance Spot balances and USD valuation. We now need to add PnL using an average buy cost.

Constraints:
- Binance Spot only.
- USDT quote currency only.
- Phase 1: buys-only average cost; ignore sells.

## Approach

### Backend
1) Determine which assets are currently displayed in the Wallet.
2) For each asset (except stablecoins / fiat), query Binance Spot executed trades for `ASSETUSDT` using `GET /api/v3/myTrades`.
3) Compute average buy cost:
   - Consider only trades with `isBuyer=true` (or equivalent).
   - Weighted average: `sum(qty * price) / sum(qty)`.
4) Return `avg_cost_usdt`, `pnl_usd`, `pnl_pct` together with current price and totals.

Performance:
- Cache prices once per request.
- Limit trade lookback window initially (configurable) and/or stop early when enough trades are fetched.
- Avoid aggressive polling; compute on page load / refresh.

### Frontend
- Add columns for Avg Cost, PnL USD, PnL %.
- Profit shown in green, loss shown in red.

## Risks
- Trade pagination/limits: myTrades is per symbol and can require paging.
- Buys-only basis can overstate PnL if the user sold a portion; accepted for phase 1.
