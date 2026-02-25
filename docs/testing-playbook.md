# Testing Playbook (crypto)

This document defines the lightweight, repeatable testing workflow for the **crypto** project.

The goal is to **reduce manual UI verification** by making automated tests part of the definition of done.

## Principles

1) **Prefer deterministic tests**
- Tests MUST not depend on external networks (Binance/CCXT, Stooq).
- Use fixtures + mocks.

2) **More integration tests, fewer E2E tests**
- Integration tests are fast and stable.
- E2E tests are valuable but can be flaky; keep them minimal.

3) **Every bug fix gets a regression test**
- If we fix a bug, we add a test that would fail before the fix.

4) **CI is the source of truth**
- If it’s not running in CI, it’s not protecting the project.

## Test Layers (what to write)

### 1) Backend integration tests (default)
**Where:** `backend/tests/integration/`

Write an integration test when:
- You add/modify an API endpoint.
- You change data source selection (stooq vs ccxt).
- You change logic that impacts `/api/opportunities` or `/api/combos/backtest`.

**Rules:**
- MUST be deterministic (no external network).
- SHOULD validate both HTTP status and key fields in the JSON payload.

**Helpers:**
- Fixtures: `backend/tests/fixtures/*.csv`
- Provider mocks + network blocker: `backend/tests/utils/market_data_mocks.py`

Example patterns:
- Assert provider selection by capturing calls in `install_market_data_provider_mock(...)`.
- Block external network via `block_external_network(monkeypatch)`.

### 2) Backend unit tests (optional)
**Where:** `tests/` or `backend/tests/unit/` (if introduced later)

Write unit tests when:
- You add pure functions (parsing, validation, inference, metrics math).

### 3) Frontend E2E tests (Playwright)
**Where:** `frontend/tests/e2e/`

Write an E2E test when:
- A UI workflow is critical and has broken before.
- The UI wiring to an API endpoint is new or changed.

**Rules:**
- Keep E2E tests minimal (aim for 3–10 total).
- Prefer mocking API responses (route interception) to avoid flakes.
- When a test fails in CI, artifacts are uploaded.

## Definition of Done (DoD) for changes

For each implemented change:

1) **At least one backend integration test** for the main new/changed behavior.
2) If UI behavior changed, add/adjust **one Playwright E2E test** only if the workflow is critical.
3) If a bug was fixed: add a **regression test**.
4) CI must be green.

## Common Recipes

### Recipe: Add an integration test for a new endpoint

1) Create test file in `backend/tests/integration/`.
2) Use `fastapi.testclient.TestClient` against `app.main.app`.
3) Monkeypatch service layer if needed.
4) Block external network.

### Recipe: Use OHLCV fixture instead of network

- Add a CSV to `backend/tests/fixtures/`.
- In test, create `FixtureMarketDataProvider` and patch `combo_routes.get_market_data_provider`.

### Recipe: Performance smoke test

- Use an integration test that asserts runtime <= threshold.
- Make threshold configurable via env var (e.g., `OPPORTUNITIES_SMOKE_MAX_SECONDS`).

## CI Notes

CI workflow is defined in `.github/workflows/ci.yml`.

- Backend tests run on push + PR.
- Playwright runs on push + PR.
- Frontend build is currently gated by `RUN_FRONTEND_BUILD` until TS issues are fixed.

## Branch Protection (recommended)

See `docs/branch-protection.md` for suggested GitHub settings.
