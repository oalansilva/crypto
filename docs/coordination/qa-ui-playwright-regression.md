# qa-ui-playwright-regression

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: in progress
- Alan homologation: not reviewed

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

## Next actions
- [x] PO: Create QA tracking card for Playwright/browser regression flows.
