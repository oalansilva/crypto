# Proposal — sincronismo e registro de tasks

## Why

Users reported that "As tasks não estão sendo exibidas nos cards aqui no kanban" (tasks are not showing on the Kanban cards). Even when clicking to open a card detail/drawer, only a few tasks appear instead of all tasks defined in tasks.md.

This reduces visibility into the progress of each change — team members cannot see what work needs to be done.

## Root Cause Analysis

After investigating:

1. **tasks.md not synced to database**: The tasks defined in the OpenSpec tasks.md file are NOT being synchronized to the workflow database (wf_work_items table).

2. **API returns empty/minimal tasks**: When calling `GET /workflow/kanban/changes/{change_id}/tasks`, it only returns tasks that were manually created in the runtime, not the ones from tasks.md.

3. **No automatic sync**: There's no sync mechanism between OpenSpec artifacts (tasks.md) and the runtime database.

4. **Impact**: All cards appear to have 0 or 1 task even though tasks.md has many more.

## What Changes

### 1. Implement tasks.md sync to runtime
- Create a sync mechanism that reads tasks from `openspec/changes/<change_id>/tasks.md`
- Parse the markdown and convert to work_items in the workflow database
- Sync happens on: card creation, card update, and before rendering

### 2. Backend API fix
- Ensure `GET /workflow/kanban/changes/{change_id}/tasks` returns all synced tasks
- Handle both parent tasks (stories) and child tasks (bugs)

### 3. Frontend
- Display all synced tasks in the drawer/card detail
- Show task progress indicator on card surface (after sync is working)

## Scope

This change covers:
- Backend: Sync tasks from tasks.md to workflow DB
- Backend: Fix API to return all synced tasks
- Frontend: Display tasks correctly

This change does not cover:
- Editing tasks from Kanban UI
- Creating new tasks from UI

## Outcome

After this change:
- All tasks from tasks.md appear when opening a card
- Task progress is visible on card surface
- No manual task entry needed - sync is automatic
