## 1. Backend

- [ ] 1.1 Add endpoint to list active changes + statuses (parse `docs/coordination/*.md`)
- [ ] 1.2 Add endpoint to return tasks checklist for a change (parse `openspec/changes/<change>/tasks.md`)
- [ ] 1.3 Add comments storage + endpoints (GET/POST per change)
- [ ] 1.4 Add tests for parsing + comments storage

## 2. Frontend

- [ ] 2.1 Add `/kanban` page
- [ ] 2.2 Render columns + cards from backend list endpoint
- [ ] 2.3 Card details panel: tasks checklist + comments thread

## 3. QA

- [ ] 3.1 Minimal E2E test: Kanban loads and shows a mocked change
- [ ] 3.2 Regression: ensure existing `/openspec` pages still work

## 4. Docs

- [ ] 4.1 Document how statuses are derived from coordination files
