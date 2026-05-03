## ADDED Requirements

### Requirement: Kanban bug E2E tests are discoverable
The Playwright E2E suite SHALL discover and list the Kanban bug regression tests from the standard E2E test directory.

#### Scenario: Playwright lists Kanban bug tests
- **WHEN** `npx playwright test --list` is executed from the frontend package
- **THEN** the output includes the `kanban-bugs.spec.ts` test cases
