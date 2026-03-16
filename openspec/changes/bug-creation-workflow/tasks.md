# Tasks: Bug Creation Workflow

## 1. Backend - Bug Type Support
- [ ] 1.1 Add `type` field to work_items (change, story, bug)
- [ ] 1.2 Add `parent_id` field to link bug to story
- [ ] 1.3 Create API endpoint to create bug linked to story

## 2. Frontend - Bug Creation UI
- [ ] 2.1 Add "Create Bug" button in story drawer
- [ ] 2.2 Create bug form (title, description, severity)
- [ ] 2.3 Link bug to parent story automatically

## 3. Workflow Rules
- [ ] 3.1 Story cannot close while open bugs exist
- [ ] 3.2 Bugs go through DEV → QA → homologation
- [ ] 3.3 QA can create bug via comment (auto-create)

## 4. Validation
- [ ] 4.1 Test bug creation from story drawer
- [ ] 4.2 Test story blocks closure with open bugs
- [ ] 4.3 Test bug flow DEV → QA → homologation
