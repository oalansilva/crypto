## 1. Implementation

- [x] Allow authenticated users to access `/favorites` and see the Favoritos nav item.
- [x] Replace tier dropdowns in Favorites with a star tier control that maps stars to `tier` values.
- [x] Hide admin-only/protected controls and raw config from common users on Favorites.
- [x] Adjust Monitor common-user filtering so tiered favorites are the visible list without portfolio/local-favorite gating.

## 2. Validation

- [x] Run OpenSpec status/validation for the change.
- [x] Run focused frontend build or tests.
- [x] Record evidence for card #126.
- [x] Fix common-user admin catalog visibility and per-user star tiers.
- [x] Align Favorites UI with the provided `crypto.2.zip` reference.

## Evidence

- `openspec validate card-126-favorites-tiers-monitor --strict` passed.
- `openspec validate --all` passed: 94 items, 0 failed.
- `npm --prefix frontend run build` passed.
- `npm --prefix frontend run test:e2e -- admin-menu-visibility.spec.ts favorites-view-results.spec.ts` passed: 6 tests.
- Integrated in `develop`: commit `65fd996`.
- Follow-up fix: common-user Favorites now lists admin catalog and stores star tiers in `monitor_strategy_preferences.tier`.
- Follow-up tests: `./backend/.venv/bin/python -m pytest backend/tests/integration/test_favorites_user_scoping.py backend/tests/integration/test_monitor_preferences_endpoints.py -q` passed: 17 tests.
- UI reference follow-up: Favorites now uses operational header, tier cards, tier chips, compact filters/search, desktop table, and mobile cards based on `crypto.2.zip`.
- UI visual check: Playwright screenshots passed for desktop 1440x960 and mobile 390x844 with no horizontal overflow on mobile (`bodyWidth=390`, `viewportWidth=390`).
