## ADDED Requirements

### Requirement: qa-gate depends on new-route Playwright coverage
For pull requests to `develop`, `qa-gate` MUST require the new-route Playwright coverage check to succeed (or an authorized visual-QA dispensation). A green functional/visual job MUST NOT hide a brand-new app route with zero specs.

#### Scenario: Coverage check is a qa-gate dependency
- **WHEN** the new-route coverage job fails
- **THEN** `qa-gate` MUST fail
