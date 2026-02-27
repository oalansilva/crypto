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
- Status → column derivation (locked, parser rules):
  - **Source-of-truth fields** (read from `docs/coordination/<change>.md`, inside `## Status`):
    - `PO:` values: `not started` | `in progress` | `blocked` | `done`
    - `DEV:` values: `not started` | `in progress` | `blocked` | `done`
    - `QA:` values: `not started` | `in progress` | `blocked` | `done`
    - Alan values (for both approval + homologation): `not reviewed` | `reviewed` | `approved`
      - Preferred explicit fields (new standard):
        - `Alan approval:` (same 3 values)
        - `Alan homologation:` (same 3 values)
      - Backward-compatible fallback: if either explicit field is missing, use `Alan (Stakeholder):` as the value for the missing field(s).
  - **Archived detection** (Archived column): a change is considered `archived=true` if **any** of the following is true:
    - The file contains a section heading exactly `## Closed` (anywhere), **or**
    - All gates are complete: `PO=done` and `DEV=done` and `QA=done` and `Alan approval=approved` and `Alan homologation=approved`.
  - **Column selection algorithm** (evaluate in this exact order; first match wins):
    1) If `archived=true` → `Archived`
    2) Else if `PO != done` → `PO`
    3) Else if `Alan approval != approved` → `Alan approval`
    4) Else if `DEV != done` → `DEV`
    5) Else if `QA != done` → `QA`
    6) Else if `Alan homologation != approved` → `Alan homologation`
    7) Else → `Archived`
  - **Representation note**: the board shows two Alan columns. The coordination file must therefore track Alan’s state separately for approval vs homologation (preferred via the two explicit fields above). If only `Alan (Stakeholder):` is present, it will be used for both.
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
  - [x] Define the exact rule for deriving each column/status from `docs/coordination/<change>.md` (source-of-truth fields and allowed values).
  - [ ] Clarify comment expectations: retention, edit/delete policy, and minimal metadata (author, timestamp).
  - [ ] Confirm scope: tasks checklist is read-only vs. interactive (check/uncheck) for v1.
  - [ ] Mark PO as **done** once above decisions are locked and documented.
- [ ] DEV: (pending Alan approval)
- [ ] QA: (pending DEV)
- [ ] Alan:
  - [ ] Review/approve: columns + mapping rules + comment persistence expectations **before DEV starts**.
