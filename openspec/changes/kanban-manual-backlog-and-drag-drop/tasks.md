## 1. Runtime / Backend

- [ ] 1.1 Add `Pending` as a first-class Kanban/workflow stage before `PO` in runtime derivation and response shapes.
- [ ] 1.2 Add a backend endpoint/service path to create a new Pending card from Kanban with title and optional description.
- [ ] 1.3 Map Kanban column moves to runtime status transitions, including `Pending -> PO` and reverse moves where allowed.
- [ ] 1.4 Return actionable validation errors when a requested move is not allowed by workflow guard rails.

## 2. Frontend Kanban UX

- [ ] 2.1 Update `/kanban` column ordering to show `Pending` before `PO` on desktop and mobile.
- [ ] 2.2 Implement a lightweight create-card flow from the Kanban page using the existing `New` affordance.
- [ ] 2.3 Add desktop drag-and-drop card movement between columns.
- [ ] 2.4 Keep the existing mobile move flow and route it through the same backend transition path as desktop drag/drop.
- [ ] 2.5 Refresh board data automatically after create/move so cards visibly change stage without manual reload.

## 3. Validation / Tests

- [ ] 3.1 Add backend tests for Pending create flow and valid/invalid column transitions.
- [ ] 3.2 Add frontend/E2E coverage for creating a Pending card from Kanban.
- [ ] 3.3 Add frontend/E2E coverage for moving a card between columns and seeing the board update automatically.

## 4. Documentation / Handoff

- [ ] 4.1 Update workflow/Kanban documentation to explain Pending backlog intake, automatic status synchronization, and that OpenSpec artifacts are created/updated when PO pulls a card from Pending into PO.
- [x] 4.2 Prepare PT-BR review notes for Alan with links to proposal, specs, design, and tasks.
- [ ] 4.3 Use project skills when applicable during implementation/testing (frontend, architecture, debugging, tests).
