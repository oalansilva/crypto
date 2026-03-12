## Why

Alan needs a lightweight way to capture backlog ideas directly in the Kanban board before PO planning starts. Today the board is mostly a read/move surface for existing changes, which creates friction for quickly adding work and managing it visually.

## What Changes

- Add a new **Pending** Kanban column for manually created backlog cards that are not yet in PO planning.
- Allow users to create a new backlog/change item directly from `/kanban` with at least a title and optional short description.
- Allow dragging cards between Kanban columns on desktop and preserving the existing mobile move flow.
- Make column moves automatically update the underlying workflow status/runtime state for the card.
- Keep Kanban as the main operational surface while PO can pull cards from **Pending** into **PO** when ready.

## Capabilities

### New Capabilities
- `kanban-backlog-intake`: Create backlog cards directly from the Kanban UI and place them in a Pending stage before PO planning.
- `kanban-drag-and-drop`: Move Kanban cards between columns with direct manipulation and automatic workflow/runtime synchronization.

### Modified Capabilities
- `kanban`: Add Pending as a first-class column and align column/status derivation with manual backlog intake and drag/drop transitions.
- `workflow-state-db`: Support a pre-PO pending workflow stage that can be created and updated from the Kanban surface.

## Impact

- Frontend: `frontend/src/pages/KanbanPage.tsx` and related UI/state handling.
- Backend: workflow Kanban endpoints and change creation/update rules in `backend/app/routes/workflow.py` plus any supporting services/models.
- Specs: Kanban and workflow-state-db behavior updates.
- Tests: backend workflow route coverage and frontend/E2E coverage for create + move flows.
