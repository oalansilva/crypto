# qa-ui-playwright-regression

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved

## Decisions (draft)
- Goal: track ongoing browser/UI QA regression flows executed with Playwright for the crypto product.
- Operational rule: use only workflow DB + Kanban comments/work items for active tracking; do not use legacy coordination as the runtime surface.
- Tooling: prefer Microsoft Playwright CLI (`playwright-cli`) plus the local adapted official skill.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/qa-ui-playwright-regression/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/qa-ui-playwright-regression/review-ptbr

## Notes
- Coordination card created automatically in the same turn as the change.
- QA handoff 2026-03-12 12:25 UTC: no new wallet product defect signal. Active blocker remains Playwright test fragility in `frontend/tests/e2e/wallet-nav.spec.ts`, where `getByText("HBAR", { exact: true })` resolves 2 visible `HBAR` nodes and trips strict mode. Next operational owner: DEV/test-maintenance to repair the selector before QA re-runs item 2.2.
- DEV follow-up 2026-03-12 18:25 UTC: selector maintenance applied in `frontend/tests/e2e/wallet-nav.spec.ts`. The asset assertions are now scoped to the `Balances` section instead of a page-global `getByText("HBAR", { exact: true })`, removing the strict-mode collision that was blocking QA. DEV reran only this spec to confirm the blocker moved past `HBAR`; runtime/Kanban was reconciled to **QA** with `QA=pending` for the next regression pass.
- QA rerun 2026-03-12 18:40 UTC: executed exactly one additional isolated wallet pass after the DEV selector fix. The prior `HBAR` strict-mode blocker no longer reproduced. The new failure happens later: the spec expects mocked `HBAR`/`USDC` rows, but the rendered wallet shows live runtime rows (`BTC`, `HBAR`, `BNB`, `USDT`), so the `USDC 0.455` assertion is missing. Evidence bundle: `qa_artifacts/playwright/wallet/recheck-2026-03-12T1840Z/{00-playwright.log,01-home.png,02-wallet-loaded.png,test-failed-1.png,error-context.md,trace.zip,video.webm,summary.json}`. Runtime should remain in **QA** with `QA=pending`; no real wallet product defect was confirmed from this turn.
- Closure note 2026-03-12 19:04 UTC: Alan requested this tracking change be finalized. Outcome recorded as completed tracking work with no confirmed wallet product defect; the residual issue is an automation/runtime-mock mismatch in `frontend/tests/e2e/wallet-nav.spec.ts`, not a released product blocker. Change can be closed and archived without opening a product bug from the current evidence.

## Next actions
- [x] PO: Create QA tracking card for Playwright/browser regression flows.
