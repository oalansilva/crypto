## 1. Frontend Flow

- [x] 1.1 Replace separate `View Trades` and `View Results` actions with one analysis CTA in desktop and mobile Favorites layouts.
- [x] 1.2 Combine backtest execution with favorite trade recovery so the result page receives consolidated metrics, chart data, and recovered trades.
- [x] 1.3 Add a non-blocking result-page warning for regenerated trade metric mismatch.

## 2. Validation

- [x] 2.1 Update Favorites E2E coverage for the single CTA and recovered trades in the result view.
- [x] 2.2 Run OpenSpec validation and focused frontend checks.

## 3. Homologation Fixes

- [x] 3.1 Add a visible return action from the favorite analysis result view back to Favorites.
- [x] 3.2 Fix trade table contrast so headers and cells remain readable.
- [x] 3.3 Extend focused E2E coverage for returning to Favorites and readable trade table rendering.

## 4. Homologation Fixes - Analysis Cache and Design Tokens

- [x] 4.1 Stop rerunning combo backtest from the favorite analysis CTA when saved trade history exists.
- [x] 4.2 Persist regenerated favorite trade history and mismatch metadata so later opens reuse saved history.
- [x] 4.3 Restyle the result trade table using `DESIGN.md` dark Binance surfaces and readable contrast.
- [x] 4.4 Extend backend and E2E coverage for cache reuse, one-time regeneration, and design-token contrast.

## 5. Homologation Fixes - Legacy Chart Cache

- [x] 5.1 Treat saved trades without `analysis_candles` as incomplete analysis cache.
- [x] 5.2 Backfill and persist chart context for legacy favorites on first analysis open.
- [x] 5.3 Extend backend/E2E coverage for BTC/USDT-style saved trades with missing chart context.

## Notes

- Use project skills when applicable: `crypto-frontend` for UI, OpenSpec skills for artifacts/apply/verify, and focused Playwright coverage for visible workflow changes.
