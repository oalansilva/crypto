## MODIFIED Requirements

### Requirement: Lab Page Title
The UI MUST stop exposing the `/lab` page entirely once the Lab functionality is removed.

#### Scenario: User tries to access /lab
- **WHEN** the user navigates to `/lab`
- **THEN** the UI MUST NOT render a Lab page

## ADDED Requirements

### Requirement: UI MUST remove Lab navigation entrypoints
The UI MUST remove visible navigation entrypoints that point to the Lab workflow.

#### Scenario: User scans global navigation
- **WHEN** the user opens the application navigation or Home shortcuts
- **THEN** the UI MUST NOT show links, buttons, or labels that navigate to the Lab workflow
