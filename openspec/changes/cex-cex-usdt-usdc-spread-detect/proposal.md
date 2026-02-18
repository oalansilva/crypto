## Why

Users want to identify low-risk CEX↔CEX stablecoin arbitrage by detecting USDT/USDC price deviations across exchanges without executing trades. This enables faster opportunity awareness and later manual or automated execution.

## What Changes

- Add a backend capability to fetch USDT/USDC prices from multiple CEXs (Binance, OKX, Bybit) and calculate cross-exchange spreads.
- Provide a single API response listing detected spreads and the best buy/sell venues for each opportunity.
- Explicitly exclude trade execution, transfers, or balance rebalancing in this feature.

## Capabilities

### New Capabilities
- `cex-cex-spread-detection`: Detect and report USDT/USDC cross-exchange spreads with configurable inputs and thresholds.

### Modified Capabilities
- 

## Impact

- Backend: new spread detection service and API endpoint.
- External dependency usage: CCXT for market data (already used in project).
- Frontend/UI: optional consumer of the API (no mandatory UI changes in this change).
