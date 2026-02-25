## Why

The current Monitor experience is useful for strategy status, but it is not optimized for **mobile trading-style monitoring** (quick price sense-making, visual trend scanning, and timeframe switching).

Alan wants a mobile-first dashboard that feels closer to a lightweight TradingView, but restricted to the symbols already in **Favorites**, using the same existing data sources.

## What Changes

- Enhance the existing **Monitor** screen by adding tabs:
  - **Status** (existing Monitor behavior)
  - **Dashboard** (new, mobile-first)
- Dashboard tab shows a compact list of favorites with quick metrics (price + change) and a **candlestick chart**.
- Allow the user to switch timeframes (e.g., 1h / 4h / 1d) per symbol.
- Reuse existing backend data sources where possible:
  - Crypto: CCXT
  - Stocks: Yahoo for intraday candles (15m/1h/4h) and Stooq/Yahoo for 1d
- For stocks intraday, apply sensible default history windows (e.g., 15m ~30d, 1h ~180d, 4h ~365d).

## Capabilities

### New Capabilities
- `monitor-dashboard-mobile`: Mobile-first trading-style dashboard for Favorites, with candlestick charts and timeframe switching.

### Modified Capabilities
- `frontend-ux`: Add responsive dashboard route and ensure mobile usability.
- `backend`: If needed, expose an API for OHLC candles for favorites (prefer reusing existing endpoints/services).

## Impact

- Frontend: new dashboard page/components, chart library integration, mobile UX.
- Backend: may require a small endpoint to provide OHLC data for a symbol/timeframe using existing providers.
- Tests: Playwright E2E for core flows (open dashboard, change timeframe, verify candles render).
