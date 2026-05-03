## Why

Issue #106 asks that common users stop seeing strategy secrets such as clear strategy names, moving-average periods, parameter values, and indicator values. The current Monitor/Favorites payloads expose enough detail for a user to reproduce the strategy outside the product.

## What Changes

- Redact strategy-identifying fields for non-admin users in backend responses.
- Restrict strategy template/backtest/optimization APIs and matching frontend routes to admin users because these surfaces expose strategy internals.
- Keep admin responses unchanged so Alan/admin can audit exact strategy names, parameters, and indicator values.
- Update Monitor UI to render protected labels and avoid showing parameter/indicator tables when the backend marks a strategy as protected.
- Add tests proving non-admin responses are redacted and admin responses keep full detail.

## Capabilities

### New Capabilities

- `strategy-secret-visibility`: Contract for exposing protected strategy data only to admin users while preserving operational buy/sell decision context for common users.

### Modified Capabilities

- `monitor`: Monitor opportunities must not expose strategy secrets to non-admin users.
- `favorites`: Favorite strategy listings must not expose strategy secrets to non-admin users.

## Impact

- Backend: `favorites` and `opportunities` routes/services, auth/admin detection, response serialization.
- Backend security: `combos` routes that expose or execute strategy templates.
- Frontend: Monitor opportunity card/chart modal rendering for protected strategy payloads and admin route guards for strategy-detail pages.
- Tests: backend unit/integration coverage for redaction and frontend build/E2E coverage where proportional.
