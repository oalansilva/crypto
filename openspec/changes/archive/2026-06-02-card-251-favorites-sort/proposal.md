## Why

The Favorites sort control changes local state, but the displayed list can remain effectively pinned by tier ordering before applying the chosen metric. Card #251 asks for the Favorites list to reorder immediately and predictably when the user selects an available sort option.

## What Changes

- Make the Favorites sort option the primary ordering key for the visible list.
- Keep deterministic tie-breakers so repeated sorting remains stable and predictable.
- Preserve existing filters, tier/star controls, responsive layout, and analysis actions.
- Add focused E2E coverage proving the sort selector changes the rendered Favorites order.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites list ordering must reflect the selected sort option immediately and consistently.

## Impact

- Frontend: `frontend/src/pages/FavoritesDashboard.tsx`
- Tests: `frontend/tests/e2e/favorites-view-results.spec.ts`
- No backend, database, dependency, or strategy-calculation changes.
