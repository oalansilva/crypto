## 1. Frontend Flow

- [x] 1.1 Replace separate `View Trades` and `View Results` actions with one analysis CTA in desktop and mobile Favorites layouts.
- [x] 1.2 Combine backtest execution with favorite trade recovery so the result page receives consolidated metrics, chart data, and recovered trades.
- [x] 1.3 Keep regenerated trade metric mismatch metadata internal and avoid showing mismatch warnings to the user.

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

## 6. Homologation Fixes - Accept Reconstructed Metrics

- [x] 6.1 Update favorite persistence so regenerated metrics become the saved summary after mismatch.
- [x] 6.2 Preserve previous metrics and deltas as investigation metadata.
- [x] 6.3 Stop showing the reconstructed-history mismatch warning after automatic reconciliation.
- [x] 6.4 Extend backend and E2E coverage for accepted reconstructed metrics.

## 7. Homologation Fixes - Remove User Mismatch Warning

- [x] 7.1 Remove the Favorites result-page mismatch warning source so legacy `metrics_match=false` payloads do not show `Histórico reconstruído pode divergir do resumo salvo.` to users.
- [x] 7.2 Keep mismatch deltas available only in favorite metrics metadata for investigation.

## Notes

- Use project skills when applicable: `crypto-frontend` for UI, OpenSpec skills for artifacts/apply/verify, and focused Playwright coverage for visible workflow changes.
