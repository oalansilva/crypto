## 1. Tracking reconciliation

- [x] 1.1 Ensure this change has OpenSpec artifacts (`proposal.md`, `tasks.md`) so Kanban/OpenSpec paths are valid.
- [x] 1.2 Keep runtime gate state aligned with the actual change stage (`QA`) and approved predecessors.

## 2. QA regression execution

- [x] 2.1 Register wallet regression evidence already produced under `qa_artifacts/playwright/wallet/`.
- [ ] 2.2 Execute one additional QA regression pass for the wallet flow and record the outcome in runtime comments.
  - Blocked in prior turn: targeted Playwright run of `frontend/tests/e2e/wallet-nav.spec.ts` failed because `getByText("HBAR", { exact: true })` matched hidden nodes in the current UI, so the automation needed selector maintenance before QA could close the regression step.
  - QA rerun 2026-03-12 10:27 UTC: blocked again by test-selector fragility, still without confirming a product defect. The current failure is a Playwright strict-mode collision: `getByText("HBAR", { exact: true })` now resolves 2 visible `HBAR` elements in the wallet UI, so the spec needs a more specific locator before QA can close this regression item. Evidence: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1027Z/{00-playwright.log,test-failed-1.png,error-context.md,trace.zip,video.webm}`.
  - QA rerun 2026-03-12 11:10 UTC: same blocker, no material product signal change. Reexecuted the isolated wallet spec and it failed at the same strict-mode collision on `getByText("HBAR", { exact: true })`, which still resolves 2 visible `HBAR` nodes in the current UI; QA still cannot confirm a wallet regression until the spec locator is narrowed. Evidence: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1110Z/{00-playwright.log,test-failed-1.png,error-context.md,trace.zip,video.webm}`.
  - QA rerun 2026-03-12 11:41 UTC: same blocker, but with a fresh isolated pass and new evidence bundle. `frontend/tests/e2e/wallet-nav.spec.ts` still fails at the same strict-mode collision on `getByText("HBAR", { exact: true })`, resolving 2 visible `HBAR` nodes in the current wallet UI; no new product defect was confirmed in this turn. Evidence: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1141Z/{00-playwright.log,test-failed-1.png,error-context.md,trace.zip,video.webm}`.
  - QA rerun 2026-03-12 12:10 UTC: blocker unchanged after one more isolated pass. `frontend/tests/e2e/wallet-nav.spec.ts` still stops on the same strict-mode collision (`getByText("HBAR", { exact: true })` resolving 2 visible `HBAR` nodes), so QA still has no confirmed wallet product defect and recommends handing this item back to DEV/test-maintenance for selector repair before another regression pass. Evidence: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1210Z/{00-playwright.log,test-failed-1.png,error-context.md,trace.zip,video.webm}`.
  - QA handoff 2026-03-12 12:25 UTC: runtime/Kanban reconciled to reflect the real blocker. QA did **not** run another identical pass in this turn because the blocker was unchanged; there is still no new product-defect signal. The next operational step is DEV/test-maintenance selector repair on `frontend/tests/e2e/wallet-nav.spec.ts` (`getByText("HBAR", { exact: true })` must be narrowed to a unique visible target), then QA can re-run item 2.2.
  - QA rerun 2026-03-12 12:42 UTC: executed one more isolated wallet regression pass and reproduced the same automation-only blocker. `frontend/tests/e2e/wallet-nav.spec.ts` still fails at `getByText("HBAR", { exact: true })` with a Playwright strict-mode collision because the current wallet UI exposes 2 visible `HBAR` nodes; QA still has no confirmed wallet product defect from this turn. Evidence: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1242Z/{00-playwright.log,test-failed-1.png,error-context.md,trace.zip,video.webm}`.

## 3. Handoff

- [x] 3.1 Leave a short QA diary/handoff comment in the runtime/Kanban thread for this turn.
