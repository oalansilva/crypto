## 1. Runtime / Backend

- [x] 1.1 Add `Pending` as a first-class Kanban/workflow stage before `PO` in runtime derivation and response shapes.
- [x] 1.2 Add a backend endpoint/service path to create a new Pending card from Kanban with title and optional description.
- [x] 1.3 Map Kanban column moves to runtime status transitions, including `Pending -> PO` and reverse moves where allowed.
- [x] 1.4 Return actionable validation errors when a requested move is not allowed by workflow guard rails.

## 2. Frontend Kanban UX

- [x] 2.1 Update `/kanban` column ordering to show `Pending` before `PO` on desktop and mobile.
- [x] 2.2 Implement a lightweight create-card flow from the Kanban page using the existing `New` affordance.
- [x] 2.3 Add desktop drag-and-drop card movement between columns.
- [x] 2.4 Keep the existing mobile move flow and route it through the same backend transition path as desktop drag/drop.
- [x] 2.5 Refresh board data automatically after create/move so cards visibly change stage without manual reload.

## 3. Validation / Tests

- [x] 3.1 Add backend tests for Pending create flow and valid/invalid column transitions.
- [x] 3.2 Add frontend/E2E coverage for creating a Pending card from Kanban.
- [x] 3.3 Add frontend/E2E coverage for moving a card between columns and seeing the board update automatically.

## 4. Documentation / Handoff

- [x] 4.1 Update workflow/Kanban documentation to explain Pending backlog intake, automatic status synchronization, and that OpenSpec artifacts are created/updated when PO pulls a card from Pending into PO.
- [x] 4.2 Prepare PT-BR review notes for Alan with links to proposal, specs, design, and tasks.
- [x] 4.3 Use project skills when applicable during implementation/testing (frontend, architecture, debugging, tests).

## 5. QA Validation

- [x] 5.1 Confirm create-card into `Pending` works in the running `/kanban` UI.
- [x] 5.2 Confirm desktop drag/drop persists across refresh and mobile long-press move sheet persists across refresh in the running app.
- [x] 5.3 Confirm invalid jumps return actionable `409` responses in the running runtime/backend (`./stop.sh && ./start.sh` refreshed the stale backend on `:8003`; revalidation now returns actionable `409` for fresh `Pending -> DEV` attempts, with evidence in `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/invalid-pending-to-dev-after-restart.json` and `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/board-after-runtime-fix.json`).
- [x] 5.4 Re-run the live runtime invalid-jump check after the refresh using a fresh `Pending` card and confirm the production backend still returns actionable `409` (`qa-pending-card-runtime-recheck-pending-1773359905`; evidence: `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/live-recheck-invalid-pending-to-dev-live.json`, `live-recheck-create-pending.json`, `live-recheck-metadata-pending.json`, `live-recheck-board-pending.json`).
- [ ] 5.5 Publish/reconcile the pending repo changes so the upstream guard allows promotion from `DEV` to `Alan homologation`; until this passes, runtime/Kanban cannot reflect the otherwise-green QA result.
