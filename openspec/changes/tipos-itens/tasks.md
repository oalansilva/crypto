# Tasks: Visual Distinction + Bug Workflow for Kanban

## Phase 1: Bug Visual Distinction

### T1: Design & Styling
- [ ] T1.1 - Define exact color scheme for bug items (contrast, accessibility)
- [ ] T1.2 - Choose visual treatment: border, background, badge, or combination
- [ ] T1.3 - Create CSS class for bug styling (e.g., `.card--bug`)

### T2: Frontend Implementation
- [ ] T2.1 - Identify Kanban card component
- [ ] T2.2 - Add conditional styling based on item type
- [ ] T2.3 - Apply bug-specific CSS
- [ ] T2.4 - Verify styling across all columns

### T3: Testing
- [ ] T3.1 - Verify bug items display correctly
- [ ] T3.2 - Confirm other types unaffected
- [ ] T3.3 - Check accessibility

## Phase 2: Bug Creation Workflow

### T4: Backend - Bug Item Support
- [ ] T4.1 - Add `type` field to work_items (change, story, bug)
- [ ] T4.2 - Add `parent_id` field to link bug to story
- [ ] T4.3 - Create API endpoint to create bug linked to story
- [ ] T4.4 - Update endpoint to list bugs by story

### T5: Frontend - Bug Creation
- [ ] T5.1 - Add "Create Bug" button in story detail/drawer
- [ ] T5.2 - Create bug form (title, description, severity)
- [ ] T5.3 - Link bug to parent story automatically

### T6: Workflow Rules
- [ ] T6.1 - Story cannot close while open bugs exist
- [ ] T6.2 - Bugs go through DEV → QA → homologation flow
- [ ] T6.3 - QA can create bug via comment (auto-create)

## Phase 3: Documentation
- [ ] D1 - Update Kanban documentation
- [ ] D2 - Document bug workflow rules
