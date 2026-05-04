## 1. Implementation

- [x] Allow authenticated users to access `/favorites` and see the Favoritos nav item.
- [x] Replace tier dropdowns in Favorites with a star tier control that maps stars to `tier` values.
- [x] Hide admin-only/protected controls and raw config from common users on Favorites.
- [x] Adjust Monitor common-user filtering so tiered favorites are the visible list without portfolio/local-favorite gating.

## 2. Validation

- [x] Run OpenSpec status/validation for the change.
- [x] Run focused frontend build or tests.
- [x] Record evidence for card #126.

## Evidence

- `openspec validate card-126-favorites-tiers-monitor --strict` passed.
- `openspec validate --all` passed: 94 items, 0 failed.
- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:e2e -- admin-menu-visibility.spec.ts favorites-view-results.spec.ts` passed: 6 tests.
- Integrated in `develop`: commit `65fd996`.
