## 1. Chart Component

- [x] 1.1 Build a Monitor-aligned reusable result chart for `/combo/results`.
- [x] 1.2 Render candles, volume, trade markers, and MA overlays from result payload data.
- [x] 1.3 Add explicit zoom controls and reset behavior without new candle fetches.

## 2. Favorites Result Integration

- [x] 2.1 Replace the legacy `CandlestickChart` usage in `ComboResultsPage`.
- [x] 2.2 Preserve the empty chart state when result candles are unavailable.
- [x] 2.3 Keep Favorites back navigation and saved analysis cache behavior unchanged.

## 3. Validation

- [x] 3.1 Extend Favorites E2E coverage for Monitor-aligned chart controls and BTC/multi MA chart visibility.
- [x] 3.2 Run OpenSpec validation, frontend build, lint, and focused E2E.

## Notes

- Use project skills when applicable: `crypto-frontend` for UI and Playwright validation, OpenSpec skills for artifacts/apply/verify.
