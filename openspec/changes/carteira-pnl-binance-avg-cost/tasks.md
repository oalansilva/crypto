## 1. Backend

- [ ] 1.1 Add Binance Spot myTrades client (signed request) with per-symbol pagination support
- [ ] 1.2 Compute avg buy cost (buys only) for each `ASSETUSDT`
- [ ] 1.3 Extend Wallet endpoint to include avg cost + PnL fields
- [ ] 1.4 Add safeguards: timeouts, max symbols per request, optional lookback window

## 2. Frontend

- [ ] 2.1 Add columns: Avg Cost (USDT), PnL (USD), PnL (%)
- [ ] 2.2 Add profit/loss coloring

## 3. Tests

- [ ] 3.1 Backend integration test with mocked Binance myTrades responses
- [ ] 3.2 Minimal Playwright E2E test for PnL rendering (mocked backend)

## 4. Ops

- [ ] 4.1 Document required Binance permissions (read-only + trade history read)
