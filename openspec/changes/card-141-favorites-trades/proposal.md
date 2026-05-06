## Why

The Favorites screen shows a trade count but `View Trades` only works when the historical trades were saved inside `metrics.trades`. Older favorites created before the database/runtime migration can keep valid summary metrics without the trade list, which makes the action look broken.

## What Changes

- Add a Favorites API path to regenerate trades for a favorite when saved trades are missing.
- Validate regenerated summary metrics against the stored favorite metrics before returning the trade list.
- Persist regenerated trades back into the favorite metrics so the screen remains consistent on future loads.
- Update the Favorites screen to request regenerated trades instead of showing "No trades saved" when the count indicates trades exist.

## Capabilities

### New Capabilities
- `favorites-trade-regeneration`: Regenerates and validates missing favorite trades from stored strategy parameters.

### Modified Capabilities
- `favorites`: `View Trades` must recover missing trade history for favorites that still have valid summary metrics.

## Impact

- Backend: `backend/app/routes/favorites.py`, `backend/app/routes/combo_routes.py`, favorite tests.
- Frontend: `frontend/src/pages/FavoritesDashboard.tsx`, Favorites E2E tests.
- API: new authenticated endpoint under `/api/favorites/{favorite_id}/trades`.
