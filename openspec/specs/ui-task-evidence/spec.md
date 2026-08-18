# ui-task-evidence Specification

## Purpose
Tasks de UI só fecham com evidência verificável contra o protótipo aprovado.

## Requirements
### Requirement: UI tasks require verifiable evidence to close
A `tasks.md` UI item MAY be marked `[x]` only with verifiable evidence (implemented file, commit, or spec). A checked UI task without matching implementation MUST NOT count as complete.

#### Scenario: Checked UI task with no code
- **WHEN** `/opsx:verify` or Code Review finds a UI task `[x]` whose described control/state is absent from the implementation
- **THEN** the finding is CRITICAL/blocking
- **AND** the task is treated as incomplete

### Requirement: Code Review checks UI tasks against the approved prototype
Code Review of a `UI impact: affected` card MUST include the checklist item "UI tasks: implemented and verified against prototype". A `[x]` without implementation is a review blocker and MUST NOT proceed to commit.

#### Scenario: Review blocks false-complete UI tasks
- **WHEN** Code Review inspects `tasks.md` against the diff and the approved prototype
- **AND** a UI task is `[x]` without the corresponding UI
- **THEN** review fails and commit is blocked

### Requirement: Verify compares UI surface to prototype before Done
`/opsx:verify` for `UI impact: affected` MUST record a comparison of the implemented surface versus the approved prototype in the handoff before Done is allowed.

#### Scenario: Verify without prototype comparison
- **WHEN** `UI impact: affected` and verify has no prototype-comparison result
- **THEN** Done is blocked

### Requirement: Open test tasks block Done
Every frontend/Playwright test task MUST be `[x]` with evidence before Done. An open `[ ]` QA/test task is a Done blocker with no silent exception.

#### Scenario: Playwright task still open at Done
- **WHEN** a Playwright or frontend test task remains `[ ]`
- **THEN** `/opsx:verify` fails and the card MUST NOT move to Done

