# Tasks — sincronismo e registro de tasks

## 1. Backend — Add task summary to kanban list
- [ ] 1.1 Add task summary fields to `KanbanChangeItem` schema (`tasks_total`, `tasks_completed`, `tasks_progress`)
- [ ] 1.2 Modify `kanban_list_changes` function to query work items per change
- [ ] 1.3 Compute task totals and completion count from `wf_work_items` table
- [ ] 1.4 Include task summary in the JSON response for each change
- [ ] 1.5 Test the updated endpoint returns task data correctly

## 2. Frontend — Update types and card UI
- [ ] 2.1 Add task fields to `CoordinationChangeItem` type in `KanbanPage.tsx`
- [ ] 2.2 Create task progress indicator component (text + optional progress bar)
- [ ] 2.3 Render task progress on card surface below title/description
- [ ] 2.4 Apply visual styling (color coding: gray/yellow/green based on progress)
- [ ] 2.5 Ensure responsive layout doesn't break on mobile

## 3. Validation / Tests
- [ ] 3.1 Test backend endpoint returns correct task counts for changes with tasks
- [ ] 3.2 Test backend handles changes with zero tasks (show 0/0 or hide indicator)
- [ ] 3.3 E2E test: verify task progress appears on Kanban cards
- [ ] 3.4 E2E test: verify task progress updates after task status changes

## 4. Documentation / Handoff
- [ ] 4.1 Update OpenSpec if new fields need documentation
- [ ] 4.2 Record handoff comment with review links
- [ ] 4.3 Close PO approval after implementation review
