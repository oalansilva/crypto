## Why

Our delivery workflow now includes a DESIGN stage for UI-related changes (HTML/CSS prototypes). The Kanban board must reflect this stage to accurately visualize flow and prevent premature DEV work.

## What Changes

- Add a **DESIGN** column to the Kanban board.
- Extend coordination parsing to include a `DESIGN` status.
- Update column derivation rules to account for DESIGN before Alan approval.

## Capabilities

### New Capabilities
- `kanban-design-column`: Visualize and manage the DESIGN stage in the Kanban flow.

### Modified Capabilities
- `kanban-visual-coordination`: Add DESIGN column and status mapping.

## Impact

- Backend: coordination parsing + column derivation rules.
- Frontend: Kanban columns order update.
- Coordination docs: template/status conventions updated.
