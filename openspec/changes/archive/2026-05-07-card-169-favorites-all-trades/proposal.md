## Why

Card #168 made Favorites sync visible trades with Monitor `signal_history`, but that changed the Favorites contract by replacing saved/regenerated history with the Monitor's shorter operational signal set.
Favorites must preserve the complete recoverable trade history because it is the review surface for saved strategies, while Monitor remains the operational current-state surface.

## What Changes

- Favorites analysis SHALL keep all saved or regenerated trades available for the selected favorite.
- Monitor `signal_history` SHALL be used only to enrich/sync current signals without reducing the recovered favorite trade set.
- The result chart opened from Favorites SHALL draw entries and exits for all trades shown in the trade list.
- Protected common-user behavior remains unchanged: no protected parameters, indicators, moving-average overlays, or technical values.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorites`: Favorites analysis must preserve all recoverable trades in the result list.
- `chart-visualization`: Result charts opened from Favorites must render markers for the same complete trade set shown in the list.

## Impact

- Frontend Favorites analysis assembly in `frontend/src/pages/FavoritesDashboard.tsx`.
- Result chart/table behavior through the existing `/combo/results` payload.
- Playwright coverage in `frontend/tests/e2e/favorites-view-results.spec.ts`.
- No backend API contract change.
