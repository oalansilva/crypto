## Why

Common users can open Favorites, but protected strategy redaction currently collapses the Strategy filter to only "Todas" and "Estratégia protegida". This prevents them from filtering the favorite catalog by strategy while reviewing protected entries.

## What Changes

- Update Favorites strategy filtering so common users receive distinct, safe strategy filter options for protected favorites.
- Show the same safe strategy name when a common user opens a protected favorite chart/analysis.
- Keep protected strategy implementation details, parameters, indicators, and raw internal names hidden from common users.
- Preserve the existing admin Favorites behavior for unprotected strategy names.
- Add focused UI coverage for the common-user protected-filter workflow.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `favorites`: Favorites Strategy filter must expose distinct protected strategy labels that are safe for common users to filter by.

## Impact

- Frontend Favorites filter option derivation, matching, and analysis handoff in `frontend/src/pages/FavoritesDashboard.tsx`.
- Existing Favorites Playwright coverage in `frontend/tests/e2e/favorites-view-results.spec.ts`.
- No API shape or database migration expected.
