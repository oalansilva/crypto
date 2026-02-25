## Why

The Favorites screen mixes crypto pairs (e.g., `BTC/USDT`) and US stock tickers (e.g., `NVDA`). On mobile and desktop this makes scanning and managing favorites slower.

A simple asset-type filter improves daily use by letting the user quickly focus on either crypto or stocks.

## What Changes

- Add an **Asset Type** dropdown filter to the Favorites screen (`/favorites`) with options:
  - All
  - Crypto
  - Stocks
- Implement classification rules:
  - Crypto: symbol contains `/` (e.g., `ETH/USDT`)
  - Stocks: symbol does not contain `/` (e.g., `AAPL`)
- Default selection: **All**.
- Filter must apply to both desktop and mobile Favorites layouts.

## Capabilities

### New Capabilities
- `favorites-asset-type-filter`: Filter Favorites by asset type (All/Crypto/Stocks).

### Modified Capabilities
- `frontend-ux`: Update Favorites UX to include the asset-type filter control.

## Impact

- Frontend: `FavoritesDashboard` and related filtering UI.
- No backend API changes expected.
