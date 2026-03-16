# Proposal: Bug Creation Workflow

## Why

Currently, there's no standardized process for creating bugs when QA finds issues:
- QA finds a bug but has no clear workflow to create it
- Stories can be closed without addressing all related bugs
- Bugs don't go through the full Kanban flow (DEV → QA → homologation)
- Bugs are shown as subtasks inside parent card, but should be separate cards

## What Changes

### Concept Change
Bugs should appear as **separate cards in the Kanban** (not subtasks), linked to parent story via `parent_id`.

### Backend Changes
1. Work_items already have `type` field (story, bug) and `parent_id`
2. Ensure bugs are returned as separate items in kanban list
3. Add filtering: kanban can show/hide bugs

### Frontend Changes
1. Add toggle to show/hide bug cards
2. Display bug cards with visual indicator linking to parent story
3. Show parent story name on bug card

### Workflow Rules
1. Story cannot close while open bugs exist
2. Bugs go through DEV → QA → homologation flow as separate cards
3. Opening a bug creates a new card, not a subtask

## Scope
- Backend: Ensure bugs appear as separate kanban items
- Frontend: Toggle to show bugs + display parent link
- Workflow: Bugs are independent cards with parent reference

## Outcome
- Bugs appear as separate cards on Kanban board
- Each bug can move through DEV → QA → homologation independently
- Parent story shows linked bugs count
