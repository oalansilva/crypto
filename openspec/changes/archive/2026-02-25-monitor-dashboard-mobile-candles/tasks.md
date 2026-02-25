## 1. Backend: Candle API

- [x] 1.1 Identify existing market data provider utilities/services that can return OHLC
- [x] 1.2 Add a backend endpoint (e.g., `GET /api/market/candles?symbol=...&timeframe=...&limit=...`) returning OHLC candles
- [x] 1.3 Implement timeframe validation:
  - stocks: 15m/1h/4h/1d (intraday via Yahoo with default history windows)
  - crypto: 15m/1h/4h/1d
- [x] 1.4 Add integration tests for the candle endpoint using deterministic fixtures/mocks (no external network)

## 2. Frontend: Monitor Tabs + Dashboard

- [x] 2.1 Add tabs to the existing Monitor screen: Status (existing) and Dashboard (new)
- [x] 2.2 Ensure existing Monitor Status view remains unchanged
- [x] 2.3 Load Favorites list and render mobile-first symbol cards (favorites-only) in the Dashboard tab
- [x] 2.4 Add symbol selection state and a detail view for the selected symbol

## 3. Candlestick Chart UI

- [x] 3.1 Add a lightweight candlestick chart library and wrapper component
- [x] 3.2 Fetch candles from the backend endpoint and render candlesticks
- [x] 3.3 Add timeframe switching controls (15m/1h/4h/1d) and update chart accordingly
- [x] 3.4 Apply default history windows for stocks intraday:
  - 15m ~30d
  - 1h ~180d
  - 4h ~365d
  - 1d ~years
  and guard unsupported combinations with clear UI feedback

## 4. UX / Performance

- [x] 4.1 Ensure no horizontal scrolling on mobile
- [x] 4.2 Ensure touch targets are >= 44x44px for primary controls
- [x] 4.3 Add sensible candle fetch limits and avoid excessive refetching

## 5. Tests (E2E)

- [x] 5.1 Add Playwright E2E test: open dashboard and see favorites list
- [x] 5.2 Add Playwright E2E test: select a symbol and see chart container
- [x] 5.3 Add Playwright E2E test: switch timeframe and verify request/visual state changes

## 6. Validation

- [x] 6.1 Run `openspec validate monitor-dashboard-mobile-candles --type change`

> Note: Use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
