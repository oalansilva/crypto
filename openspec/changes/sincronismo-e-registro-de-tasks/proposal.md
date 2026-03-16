# Proposal — sincronismo e registro de tasks

## Why

Users reported that "As tasks não estão sendo exibidas nos cards aqui no kanban" (tasks are not showing on the Kanban cards). This reduces visibility into the progress of each change — team members must click into each card to see what tasks exist and their completion status.

The Kanban board should provide at-a-glance task progress on the card surface, similar to how task lists work in other project management tools (e.g., GitHub PRs showing "2/5 checks", Trello cards showing checklist progress).

## Root Cause Analysis

After reviewing the codebase:

1. **Card surface lacks task data**: The Kanban list endpoint (`GET /workflow/kanban/changes`) returns card metadata (id, title, description, status, column, position) but does NOT include any task/checklist summary.

2. **Tasks are fetch-on-demand only**: Tasks are only loaded when a user clicks to open a card detail drawer (`GET /workflow/kanban/changes/{change_id}/tasks`). This is a separate API call that only happens after card selection.

3. **No task count/progress field**: The `KanbanChangeItem` schema in the backend has no field for task summary (total tasks, completed count, or progress percentage).

4. **Frontend doesn't render task info on card**: The `KanbanPage.tsx` card template only displays: title, ID, description snippet, and status lines. There's no UI component for task progress.

## What Changes

### Backend
- Add task summary fields to `KanbanChangeItem`:
  - `tasks_total`: Total number of tasks (stories + bugs)
  - `tasks_completed`: Number of completed tasks
  - `tasks_progress`: Percentage or fraction (e.g., "3/5" or "60%")
- Modify `kanban_list_changes` to query work items and compute task summary for each change
- Ensure the data is included in the JSON response

### Frontend
- Update `CoordinationChangeItem` type in `KanbanPage.tsx` to include new task fields
- Add task progress indicator to the card surface:
  - Show "X/Y tasks" text or progress bar
  - Display completed vs total (e.g., "✓ 3/5")
  - Use color coding: gray for 0%, yellow for partial, green for complete
- Ensure the indicator is visible but doesn't clutter the card

### Data Flow
- Backend queries `wf_work_items` table for each change
- Computes: `total = stories + bugs`, `completed = where state in (done, canceled)`
- Returns aggregated data in the kanban list response
- Frontend renders directly from list response (no additional API calls needed)

## Scope

This change covers:
- Backend: Add task summary to kanban list endpoint
- Frontend: Display task progress on card surface
- Data: Query existing work items from workflow DB

This change does not cover:
- Creating/editing tasks from the Kanban UI (future enhancement)
- Task detail view in the drawer (already exists)
- Push notifications for task updates
- Bulk operations on tasks

## Outcome

After this change:
- Each Kanban card displays task progress at a glance (e.g., "✓ 3/5")
- Team members can quickly assess which cards are ready for review vs. still in progress
- No extra clicks required to see task status
- Visual consistency with standard project management tools
