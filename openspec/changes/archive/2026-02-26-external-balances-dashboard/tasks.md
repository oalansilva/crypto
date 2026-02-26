## 1. Backend

- [ ] 1.1 Add server-side Binance client helper (signed request, read-only)
- [ ] 1.2 Add endpoint: `GET /api/external/binance/spot/balances`
- [ ] 1.3 Ensure missing-secret errors are clear and secrets are not logged

## 2. Frontend

- [ ] 2.1 Add page/route (e.g., `/external/balances`) and navigation entry
- [ ] 2.2 Render balances list with free/locked/total and highlight locked amounts

## 3. Tests

- [ ] 3.1 Add a backend integration test with mocked Binance HTTP response
- [ ] 3.2 Add a minimal Playwright E2E test for the new page (mocked backend)

## 4. Ops

- [ ] 4.1 Document required env vars and deployment steps

> Note: use existing project skills/tools (.codex/skills) for debugging and validation where applicable.
