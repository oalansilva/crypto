## Why

The project currently relies heavily on manual UI verification, which is slow and error-prone. Regressions like incorrect market-data provider selection (e.g., US ticker routed to Binance/CCXT) can slip through and only be discovered during manual use.

We want fast, deterministic automated checks that run on every push/PR and provide actionable artifacts when failures occur.

## What Changes

- Add a GitHub Actions CI workflow that runs backend tests and (optionally) frontend checks.
- Introduce deterministic test fixtures and provider mocking so tests do not depend on external networks (Binance/Stooq).
- Add integration tests for critical API flows (combos backtest, opportunities).
- Add a minimal Playwright E2E suite for core UI flows (Favorites -> View Results).
- Upload CI artifacts (Playwright traces/screenshots, logs) to speed up debugging.

## Capabilities

### New Capabilities
- `ci-testing-hardening`: A reliable, automated test pipeline (unit/integration/E2E) with deterministic data and useful artifacts.

### Modified Capabilities
- `backend`: Add integration tests and test-only provider injection/mocking.
- `frontend-ux`: Add minimal E2E coverage for the Favorites workflow.

## Impact

- Repo: add `.github/workflows/ci.yml`.
- Backend tests: new fixtures + integration tests.
- Frontend tests: Playwright setup + 1-3 E2E tests.
- Optional: recommend enabling branch protection rules in GitHub settings.
