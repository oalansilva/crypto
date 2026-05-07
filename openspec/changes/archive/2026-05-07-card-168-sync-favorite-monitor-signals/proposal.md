## Why

Favorites can now render current candles, but its entry/exit markers can still come from saved favorite trades while Monitor uses current operational `signal_history`. Users comparing both screens can see different buy/sell points for the same symbol/timeframe and lose trust in the workflow.

## What Changes

- Synchronize Favorites analysis with Monitor signal history before rendering the result chart/trade list.
- Use current Monitor/opportunities signal history as the primary source for entry/exit markers when available.
- Preserve saved favorite metrics/trades as stored favorite evidence and fallback.
- Keep protected common-user redaction intact while allowing safe entry/exit history already exposed by Monitor.
- Add E2E coverage where saved favorite trades diverge from Monitor history and opening Favorites analysis uses Monitor-synced entries/exits.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorites`: Favorites analysis must synchronize current entry/exit signals with Monitor before rendering analysis.
- `chart-visualization`: Result charts opened from Favorites must prefer current Monitor signal history for entry/exit markers.

## Impact

- Frontend:
  - `frontend/src/pages/FavoritesDashboard.tsx`
  - `frontend/src/pages/ComboResultsPage.tsx` behavior through result state data.
- Tests:
  - Favorites E2E coverage for stale saved trades replaced by Monitor signal history.
- Backend:
  - No new endpoint expected; uses existing `/api/opportunities/?refresh=true` as the current operational source.
