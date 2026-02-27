# kanban-visual-coordination

## Status
- PO: in progress
- DEV: not started
- QA: not started
- Alan (Stakeholder): not reviewed

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Add a visual Kanban board inside the web app so Alan can easily track progress across active changes, view the task checklist, and read/write comments.
- Surface (mobile/desktop): Web app (desktop-first). Scope is internal coordination UI.
- Defaults:
  - Column set (ordered): PO → Alan approval → DEV → QA → Alan homologation → Archived.
  - Archived handling: archived changes are **always listed** (not optional).
  - Cards: each change is one card; board shows active + archived.
- Data sources:
  - Statuses and “next step” come from `docs/coordination/*.md` (Status section).
  - Checklist comes from OpenSpec `openspec/changes/<change>/tasks.md`.
- Persistence:
  - Comments are stored server-side (keyed by change), via backend GET/POST endpoints.
  - Coordination + tasks remain file-based (markdown) and are read-only from the UI (no editing required for v1).
- Performance limits: Must handle the typical number of active changes (small/medium) with fast initial load; no heavy optimization required for v1.
- Non-goals:
  - No changes to trading/backtest logic.
  - No attempt to replace OpenSpec; this is a visualization layer.

## Links
- OpenSpec viewer: (placeholder) /openspec/changes/kanban-visual-coordination
- PT-BR review (viewer): (placeholder) /openspec/changes/kanban-visual-coordination/review-ptbr
- PR:
- CI run:

## Notes
- The Kanban UI should make the existing markdown workflow easier to consume (no new process).

## Next actions
- [ ] PO:
  - [x] Confirm final column set + mapping to existing workflow (Archived is a column and is always listed).
  - [ ] Define the exact rule for deriving each column/status from `docs/coordination/<change>.md` (source-of-truth fields and allowed values).
  - [ ] Clarify comment expectations: retention, edit/delete policy, and minimal metadata (author, timestamp).
  - [ ] Confirm scope: tasks checklist is read-only vs. interactive (check/uncheck) for v1.
  - [ ] Mark PO as **done** once above decisions are locked and documented.
- [ ] DEV: (pending Alan approval)
- [ ] QA: (pending DEV)
- [ ] Alan:
  - [ ] Review/approve: columns + mapping rules + comment persistence expectations **before DEV starts**.
