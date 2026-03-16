# Proposal: Bug Creation Workflow

## Why

Currently, there's no standardized process for creating bugs when QA finds issues:
- QA finds a bug but has no clear workflow to create it
- Stories can be closed without addressing all related bugs
- Bugs don't go through the full Kanban flow (DEV → QA → homologation)

## What Changes

### Backend Changes
1. Add `type` field to work_items (change, story, bug)
2. Add `parent_id` field to link bug to story
3. Create API endpoint to create bug linked to story

### Frontend Changes
1. Add "Create Bug" button in story detail/drawer
2. Create bug form (title, description, severity)
3. Link bug to parent story automatically

### Workflow Rules
1. Story cannot close while open bugs exist
2. Bugs go through DEV → QA → homologation flow
3. QA can create bug via comment (auto-create)

## Scope
- Backend: Add bug type + parent link to work_items
- Frontend: Bug creation UI in story drawer
- Workflow: Enforce bug blocking story closure
