# delivery-qa-stage Specification

## Purpose
Define the mandatory delivery workflow that places automated QA between Code Review and Done technical.

## Requirements

### Requirement: Delivery workflow MUST include an explicit QA stage
The delivery workflow MUST use `Todo → In Progress → Code Review → QA → Done → Homologado → Pronto` as its normal forward path. `Status` MUST remain the primary board field, and the QA stage MUST appear between Code Review and Done.

#### Scenario: Reviewed delivery enters QA
- **WHEN** the exact implementation diff has passed Code Review and its reviewed commit is available for validation
- **THEN** the card MUST move to `Status=QA` before it can be reported as Done

### Requirement: QA MUST gate Done technical
A card MUST NOT move to Done until required QA checks have reached a terminal successful result, the work is integrated in develop, and the documented runtime reconciliation has completed.

#### Scenario: QA checks are still running or failing
- **WHEN** any required QA check is running, cancelled, skipped without an authorized dispensation, or failing
- **THEN** the card MUST remain outside Done and report the blocking evidence

#### Scenario: QA and runtime evidence are complete
- **WHEN** QA is green, the reviewed work is integrated in develop, `./restart` has completed, and the system URL serves the new result
- **THEN** the card MAY move to Done technical with the corresponding evidence

### Requirement: QA failures MUST return delivery work to the review cycle
Failures that require a code or artifact change MUST return the card to In Progress, followed by Code Review and a new QA execution. A card that already reached Done MUST retain its current Status while the correction is revalidated.

#### Scenario: QA finds a fixable regression before Done
- **WHEN** QA reports a regression that requires a source change before the card reaches Done
- **THEN** the card MUST follow `QA → In Progress → Code Review → QA`

#### Scenario: A Done card requires a corrective retest
- **WHEN** a corrective change is needed after the card is already Done
- **THEN** the card MUST keep its Done Status while the correction and retest evidence are recorded

### Requirement: QA evidence MUST be auditable
The QA handoff MUST record the tested commit or run, executed checks, visual artifacts when applicable, Code Review result, and remaining next action.

#### Scenario: QA handoff is published
- **WHEN** QA completes successfully or fails
- **THEN** the card or linked pull request MUST expose a concise evidence summary and links to relevant CI artifacts

### Requirement: QA cannot close Done on a new route without Playwright evidence
A card that adds a product route MUST NOT move to Done while the route lacks functional+visual Playwright coverage, unless Alan recorded the auditable visual-QA dispensation.

#### Scenario: Done blocked without spec
- **WHEN** the delivery added a new `App.tsx` route and no spec or dispensation exists
- **THEN** the card MUST remain outside Done

### Requirement: Code Review evidence MUST include the local reviewer results
QA handoff and Done technical evidence SHALL include the `diff-reviewer` and `code-reviewer` outcomes for the reviewed SHA, in addition to the existing QA checks, visual artifacts and next action.

#### Scenario: QA handoff cites local reviewers
- **WHEN** QA or Done evidence is published
- **THEN** the summary MUST include the `diff-reviewer` result (uncommitted and versus `develop`) and the `code-reviewer` result (findings, no findings, classified residuals, or spawn-failed plus fallback)

### Requirement: Paid Cursor Bugbot is not the pre-commit Code Review gate
Automatic Cursor Bugbot on the pull request to `develop` MUST remain Off unless Alan later enables it. It MUST NOT replace the pre-commit local reviewers. Enabling the paid product is out of scope for this change.

#### Scenario: Paid Bugbot stays off
- **WHEN** a pull request to `develop` is opened after local Code Review
- **THEN** the local `diff-reviewer` and `code-reviewer` remain the Code Review gate
- **AND** the agent MUST NOT treat a missing Cursor Bugbot check as a QA failure

### Requirement: Autofix MUST NOT commit to the existing PR branch
If Bugbot is later enabled, Autofix MUST remain Off for this repository, or at most create a new branch. Autofix MUST NOT commit onto the existing reviewed branch. Agent Review MUST NOT run automatically after every commit.

#### Scenario: Autofix on existing branch is forbidden
- **WHEN** a reviewer reports findings
- **THEN** a Cloud Agent MUST NOT push fixes to the existing PR branch as Autofix
- **AND** Agent Review automatic-after-commit MUST remain disabled
