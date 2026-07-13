## ADDED Requirements

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
