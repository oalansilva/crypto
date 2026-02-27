## 1. Backend

- [ ] 1.1 Add endpoint to list active + archived changes + statuses (parse `docs/coordination/*.md`)
- [ ] 1.2 Add endpoint to return tasks checklist for a change (parse `openspec/changes/<change>/tasks.md`)
- [ ] 1.3 Add comments storage + endpoints (GET/POST per change)
- [ ] 1.4 Add tests for parsing + comments storage

## 2. Frontend

- [ ] 2.1 Add `/kanban` page
- [ ] 2.2 Render the ordered columns + cards from backend list endpoint (includes active + archived; no archived toggle)
- [ ] 2.3 Card details panel: tasks checklist + comments thread
- [ ] 2.4 Add Archived as the final column (always listed; no filter/toggle)

## 3. QA

- [ ] 3.1 Minimal E2E test: Kanban loads and shows a mocked change
- [ ] 3.2 Regression: ensure existing `/openspec` pages still work

## 4. Docs

- [ ] 4.1 Document the status→column derivation rules (source-of-truth fields, allowed values, Archived detection, Alan approval vs homologation) as locked in docs/coordination/kanban-visual-coordination.md
