# kanban-visual-coordination

## Status
- PO: done
- DEV: in progress
- QA: not started
- Alan approval: approved
- Alan homologation: not reviewed
- Alan (Stakeholder): approved

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
  - Tasks checklist behavior (v1): **read-only display** (no check/uncheck in the UI).
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
  - Comment policy (v1):
    - Retention: keep comments indefinitely (including after a change is Archived).
    - Edit/delete: **not supported** in v1 (append-only thread).
    - Minimal metadata per comment: `id`, `change`, `author`, `created_at` (UTC ISO-8601), `body`.
    - Constraints: `body` is plain text (no Markdown parsing in v1), max length 2,000 chars.
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
- DEV is blocked pending Alan approval.

## Alan approval instructions
To approve and unblock DEV, update this same file:
- In `## Status`, set: `Alan approval: approved`

Review criteria (what you are approving):
- Column set + order: `PO → Alan approval → DEV → QA → Alan homologation → Archived`
- Status → column derivation rules (source-of-truth fields + allowed values + evaluation order)
- Archived detection rules
- Comment persistence expectations (append-only, retention, no edit/delete in v1)
- Tasks checklist behavior in the Kanban UI: read-only display (v1)

## Next actions
- [ ] **Alan approval (required to start DEV):** After review, set `Alan approval: approved` in the `## Status` section of this file.
- [x] PO:
  - [x] Confirm final column set + mapping to existing workflow (Archived is a column and is always listed).
  - [x] Define the exact rule for deriving each column/status from `docs/coordination/<change>.md` (source-of-truth fields and allowed values).
  - [x] Clarify comment expectations: retention, edit/delete policy, and minimal metadata (author, timestamp).
  - [x] Confirm scope: tasks checklist is read-only vs. interactive (check/uncheck) for v1.
  - [x] Mark PO as **done** once above decisions are locked and documented.
- [ ] DEV:
  - [x] Backend 1.1: Add endpoint to list active + archived changes + statuses (parse `docs/coordination/*.md`)
  - [x] Backend 1.2: Add endpoint to return tasks checklist for a change (parse `openspec/changes/<change>/tasks.md`)
  - [x] Backend 1.3: Add comments storage + endpoints (append-only)
  - [x] Backend 1.4: Add tests for parsing + comments storage
  - [ ] Frontend 2.1-2.4: Add /kanban page + columns/cards + details panel (tasks + comments)
- [ ] QA: (pending DEV)
