## Why

The Favorites strategy filter is built from the favorite display name. Saved favorite names can include symbol and timeframe context, so the Strategy dropdown can show entries with hours/timeframes instead of only the strategy name.

## What Changes

- Build the Favorites Strategy filter from the strategy label, not the favorite name.
- Keep timeframe filtering separate in the existing Time dropdown.
- Preserve the existing table/card display names; only the filter option source and matching rule change.
- Add focused E2E coverage so Strategy options do not include symbol/timeframe text.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites Strategy filter options and matching use only the strategy label.

## Impact

- `frontend/src/pages/FavoritesDashboard.tsx`
- `frontend/tests/e2e/favorites-view-results.spec.ts`
