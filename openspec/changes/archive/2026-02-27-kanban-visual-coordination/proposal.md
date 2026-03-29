## Why

Today the workflow kanban lives in markdown files (`docs/coordination/*.md`) and OpenSpec task lists (`openspec/changes/<change>/tasks.md`). This is automation-friendly, but not visually easy for Alan to track progress and read comments.

## What Changes

- Add a **visual Kanban board** inside the existing web app.
- Show each active change as a card and map it to our workflow columns:
  - PO
  - Alan approval
  - DEV
  - QA
  - Homologation
  - Archived (optional view)
- Provide a **card details panel** that shows:
  - current status + next step
  - a checklist view of OpenSpec `tasks.md`
  - a comments thread for that change

## Capabilities

### New Capabilities
- `kanban-visual-coordination`: Visualize coordination + tasks + comments in a Kanban UI.

### Modified Capabilities
- (none)

## Impact

- Frontend: new Kanban page + components.
- Backend: endpoints to read coordination and tasks, and to store comments.
- No changes to trading/backtest logic.
