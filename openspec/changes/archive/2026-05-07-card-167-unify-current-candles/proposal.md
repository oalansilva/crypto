## Why

Favorites analysis can render stale candles while Monitor renders the current market window for the same symbol/timeframe. This creates conflicting chart evidence for the same asset and makes saved favorites look outdated even when the market candle store is current.

## What Changes

- Use the current market candles source as the primary chart source for Favorites analysis and `/combo/results` entries opened from Favorites.
- Preserve saved favorite trades and metrics as the audit/summary source.
- Keep saved `metrics.analysis_candles` only as a fallback when current market candles cannot be loaded.
- Preserve protected common-user behavior: users can see the current candle map, but not moving averages, MA values, indicators, or protected parameters.
- Add focused tests proving stale saved favorite candles are replaced by current `/market/candles` candles for chart rendering.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorites`: Favorites analysis chart rendering must prefer current market candles over stale saved analysis candles.
- `chart-visualization`: Result chart surfaces opened from Favorites must use a shared current candle source and fallback consistently.

## Impact

- Frontend:
  - `frontend/src/pages/FavoritesDashboard.tsx`
  - result chart navigation state for `/combo/results`
- Tests:
  - Favorites E2E coverage around stale saved candles and current market candles.
- Backend:
  - No API contract change expected; existing `/api/market/candles` remains the canonical current candle endpoint for UI charts.
