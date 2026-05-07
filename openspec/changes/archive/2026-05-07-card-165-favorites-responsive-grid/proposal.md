## Why

The Favorites desktop table currently forces horizontal scrolling because it keeps a wide fixed minimum width. Card #165 asks for the Favorites grid to fit common desktop and mobile viewports without making horizontal scroll the normal workflow.

## What Changes

- Make the Favorites desktop table responsive by prioritizing essential columns and hiding advanced metric columns at narrower desktop breakpoints.
- Preserve the existing mobile card layout below the tablet/desktop breakpoint.
- Keep advanced data available through the existing analysis/export flows and on wider screens.
- Add E2E coverage that checks the Favorites route does not overflow horizontally on desktop and mobile.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites list layout must avoid horizontal scrolling in common desktop and mobile viewports while preserving primary fields and actions.

## Impact

- Frontend: `frontend/src/pages/FavoritesDashboard.tsx`, `frontend/src/index.css`
- Tests: `frontend/tests/e2e/favorites-view-results.spec.ts`
- Design: applies `DESIGN.md` dark Binance-style tokens already used by the Favorites workbench; no API, database, or dependency changes.
