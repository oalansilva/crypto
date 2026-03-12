# kanban-manual-backlog-and-drag-drop

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions
- `Pending` becomes a first-class pre-PO runtime/Kanban column.
- New cards can be created directly from `/kanban` with title + optional short description.
- Desktop uses drag-and-drop; mobile keeps the current move flow, both backed by the same runtime transition path.
- Runtime/Kanban is the operational source of truth for newly created `Pending` cards.
- OpenSpec artifacts for intake cards are created/updated when PO pulls a card from `Pending` into `PO`, not at raw backlog intake time.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/review-ptbr

## Notes
- Coordination card created automatically in the same turn as the change.

## Next actions
- [ ] Alan: Review proposal/spec/design/tasks and approve PO scope.
- [ ] DEV: Implement Pending intake, shared move transitions, desktop drag-and-drop, and board auto-refresh after approval.
- [ ] QA: Validate Pending creation, desktop drag/drop, mobile move parity, and runtime synchronization after DEV.
