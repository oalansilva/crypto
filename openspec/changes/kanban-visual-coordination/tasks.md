> Prereq satisfied: `docs/coordination/kanban-visual-coordination.md` already has `Alan approval: approved` in its `## Status` section.

## 1. Backend

- [x] 1.1 Add endpoint to list active + archived changes + statuses (parse `docs/coordination/*.md`)
- [x] 1.2 Add endpoint to return tasks checklist for a change (parse `openspec/changes/<change>/tasks.md`)
- [x] 1.3 Add comments storage + endpoints (append-only)
  - Data model: id, change, author, created_at (UTC ISO-8601), body
  - Validation: body max length 2,000 chars
  - API: list comments (GET) + create comment (POST). No edit/delete in v1.
- [x] 1.4 Add tests for parsing + comments storage
- [x] 1.5 Seed comments thread automatically when none exists (create first system comment)

## 2. Frontend

- [x] 2.1 Add `/kanban` page
- [x] 2.2 Render the ordered columns + cards from backend list endpoint (includes active + archived; no archived toggle)
- [x] 2.3 Card details panel: tasks checklist (read-only in v1) + comments thread
  - Comments UI shows author + timestamp; create-only (no edit/delete)
- [x] 2.4 Add Archived as the final column (always listed; no filter/toggle)
- [x] 2.5 Tasks UI: child items without explicit checkbox should inherit parent completion state (avoid confusion)

## 3. QA

- [x] 3.1 Minimal E2E test: Kanban loads and shows a mocked change
- [x] 3.2 Regression: ensure existing `/openspec` pages still work

## 4. Docs

- [x] 4.1 Document the status→column derivation rules (source-of-truth fields, allowed values, Archived detection, Alan approval vs homologation) as locked in docs/coordination/kanban-visual-coordination.md
