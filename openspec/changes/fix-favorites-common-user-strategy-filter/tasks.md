## 1. Backend Redaction Contract

- [x] 1.1 Update protected Favorites redaction to return a safe distinct `strategy_display_name` while keeping `strategy_name` and `parameters` redacted.
- [x] 1.2 Add or update backend tests for common-user Favorites listing.

## 2. Frontend Filter Behavior

- [x] 2.1 Keep Favorites Strategy filter options and matching based on the safe strategy label.
- [x] 2.2 Keep Favorites analysis/chart handoff based on the same safe strategy label for protected common-user favorites.
- [x] 2.3 Update Playwright coverage so a common/protected favorite can be filtered by a safe strategy label, shows that label in the chart, and not by symbol, timeframe, or nickname.

## 3. Validation

- [x] 3.1 Run focused backend and frontend tests for Favorites.
- [x] 3.2 Run OpenSpec validation for `fix-favorites-common-user-strategy-filter`.

Note: use project skills when applicable: `crypto-frontend` for UI changes and OpenSpec skills for artifact/apply/verify flow.
