# kanban-add-design-column

## Status
- PO: done
- Alan approval: approved
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions (locked)
- Add DESIGN as always-visible column: PO → DESIGN → Alan approval → DEV → QA → Alan homologation → Archived.
- Coordination supports `DESIGN:` status with values: not started | in progress | blocked | done | skipped.
- Backward compatibility: missing DESIGN defaults to skipped.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/kanban-add-design-column/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/kanban-add-design-column/review-ptbr

## Next actions
- [x] PO: Done
- [ ] DEV: Implement backend+frontend+tests for DESIGN column
- [ ] QA: Validate and run E2E
- [ ] Alan: Homologate
