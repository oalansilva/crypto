## Context

The repo currently relies on manual verification for key flows (Favorites, backtest results). Several production issues have been caused by implicit defaults, network dependencies, and the absence of automated regression coverage.

Constraints:
- CI should be fast and deterministic.
- Network calls to Stooq and CCXT/Binance should not be required for tests.
- E2E coverage should be minimal but high value.

## Goals / Non-Goals

**Goals:**
- Add a GitHub Actions CI pipeline with backend tests and minimal E2E checks.
- Make backend tests deterministic via fixtures and mocking of market data providers.
- Add integration tests that specifically catch data source selection regressions.
- Upload artifacts (Playwright trace/screenshot) on failures.
- Add a simple API-level performance smoke test for `/api/opportunities`.

**Non-Goals:**
- Achieve full test coverage across the entire system.
- Add extensive UI snapshot coverage.
- Redesign the backend architecture.

## Decisions

1) Use GitHub Actions as the primary CI
- Rationale: Native integration, easy status checks, artifact upload, branch protection support.

2) Deterministic market data via fixtures + provider mocking
- Decision: For backend tests, avoid external dependencies by monkeypatching provider selection (`get_market_data_provider`) and returning fixture dataframes.
- Rationale: Eliminates flakes and speeds up CI.

3) Minimal E2E with Playwright
- Decision: Add 1-3 Playwright tests that exercise Favorites -> View Results.
- Rationale: Catches UI routing + API wiring regressions with minimal maintenance.

4) Performance smoke test as integration test
- Decision: Add an integration test with a configurable threshold (e.g., <= 10s) for opportunities when using mocked data.
- Rationale: Prevents accidental CPU-heavy loops from shipping.

5) Branch protection as a recommended operational step
- Decision: Document/enable required checks in GitHub settings.
- Rationale: Prevents broken code from landing on main.

## Risks / Trade-offs

- [Risk] Mocking can diverge from real providers → Mitigation: keep a small set of optional “networked” tests disabled by default.
- [Risk] E2E flakiness → Mitigation: keep tests minimal, use stable selectors, upload trace artifacts.
- [Risk] CI runtime creep → Mitigation: limit E2E suite, keep fixtures small.

## Migration Plan

1) Add CI workflow running backend tests.
2) Add fixtures + mocking utilities.
3) Add integration tests for combos backtest data_source selection + opportunities performance.
4) Add Playwright E2E suite + artifact upload.
5) Enable branch protection in GitHub settings (required checks).

Rollback: revert the CI workflow commit(s) if it blocks development; tests are additive.

## Open Questions

- Should `npm run build` be included immediately, given existing TS build failures in some paths?
- What performance threshold is acceptable for `/api/opportunities` under typical (mocked) workloads?
