## ADDED Requirements

### Requirement: Incomplete QA tasks block card close
`/opsx:verify` and Done technical SHALL fail when any test/QA task in `tasks.md` is still `[ ]`, or when a UI task is `[x]` without implementation evidence.

#### Scenario: False-complete UI checklist
- **WHEN** UI tasks are `[x]` but the described UI is missing
- **THEN** card close is blocked

#### Scenario: Open Playwright task
- **WHEN** a Playwright task is `[ ]` at Done
- **THEN** card close is blocked
