# Tasks — sincronismo e registro de tasks

## 1. Backend — Implement tasks.md sync to workflow DB
- [ ] 1.1 Create a function to parse tasks.md and extract task structure
- [ ] 1.2 Implement sync logic: read tasks.md → create/update work_items in wf_work_items
- [ ] 1.3 Trigger sync on: card creation, card update, before rendering tasks API
- [ ] 1.4 Handle parent tasks (stories) and child tasks (bugs) properly
- [ ] 1.5 Test sync with existing cards

## 2. Backend — Fix tasks API
- [ ] 2.1 Update `GET /workflow/kanban/changes/{change_id}/tasks` to return all synced tasks
- [ ] 2.2 Ensure parent/child relationship is preserved
- [ ] 2.3 Test API returns all tasks after sync

## 3. Frontend — Display tasks correctly
- [ ] 3.1 Verify all tasks appear in drawer/card detail
- [ ] 3.2 Add task progress indicator on card surface (optional, after sync works)

## 4. Validation
- [ ] 4.1 Test: open card "alterar-dados-dos-cards" → should show all 12 tasks
- [ ] 4.2 Test: create new card → tasks.md should sync automatically
- [ ] 4.3 Test: update tasks.md → changes should reflect in Kanban
