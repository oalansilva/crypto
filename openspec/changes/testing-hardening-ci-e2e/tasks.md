## 1. CI Workflow (GitHub Actions)

- [ ] 1.1 Add `.github/workflows/ci.yml` to run backend tests on push + pull_request
- [ ] 1.2 Add artifact upload step for E2E failures (trace/screenshot)
- [ ] 1.3 Decide whether to include frontend build in CI immediately (or gate behind a flag until TS build is clean)

## 2. Deterministic Market Data for Tests

- [ ] 2.1 Add OHLCV fixtures for at least one US ticker (e.g., NVDA 1d) and one crypto pair (e.g., BTC/USDT 1d)
- [ ] 2.2 Add a test utility to mock `get_market_data_provider` and return fixture dataframes (no network)

## 3. Backend Integration Tests

- [ ] 3.1 Add integration test for `POST /api/combos/backtest` ensuring US tickers default to stooq when data_source is omitted
- [ ] 3.2 Add integration test for crypto pair backtest ensuring ccxt selection (mocked)
- [ ] 3.3 Add smoke/performance test for `GET /api/opportunities/?tier=all` with a target duration (configurable)

## 4. Frontend E2E (Playwright)

- [ ] 4.1 Add Playwright setup/config and install dependencies
- [ ] 4.2 Add E2E test: open `/favorites` and ensure the list renders
- [ ] 4.3 Add E2E test: Favorites -> View Results navigates to results without errors (mock or test backend)

## 5. Branch Protection (Operational)

- [ ] 5.1 Document required branch protection settings for `main` (require CI checks, require PR)

> Note: Use project skills (.codex/skills) when applicable for tests, debugging, and frontend work.
