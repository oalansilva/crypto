# kanban-add-design-column

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved


## Closed

- Homologated by Alan and archived.

## Decisions (locked)
- Add DESIGN as always-visible column: PO → DESIGN → Alan approval → DEV → QA → Alan homologation → Archived.
- Coordination supports `DESIGN:` status with values: not started | in progress | blocked | done | skipped.
- Backward compatibility: missing DESIGN defaults to skipped.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/kanban-add-design-column/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/kanban-add-design-column/review-ptbr

## Next actions
- [x] PO: Done
- [x] DEV: Implement backend+frontend+tests for DESIGN column
- [x] QA: Validate and run E2E (pytest integration + Playwright)
- [ ] Alan: Homologate

## Comments
- No @QA mentions found on this card.
