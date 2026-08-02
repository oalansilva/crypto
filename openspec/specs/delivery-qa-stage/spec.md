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

### Requirement: QA MUST be accepted by Sol High
The QA stage MUST be conducted by the Sol High primary session against the exact reviewed SHA and MUST include inspection of the implementation, OpenSpec artifacts, review result, and all mandatory automated evidence. Application runtime evidence means the DEV service/URL health required by the project; it does not mean pre-spawning model-routing lanes.

#### Scenario: Reviewed SHA enters QA
- **WHEN** the applicable independent review has no blocking unclassified findings on the exact diff and that content is committed and pushed — a read-only Codex review for the bootstrap change, or the fresh Luna reviewer after profile activation
- **THEN** Sol High runs `/opsx:verify`, evaluates terminal checks and decides whether QA passes or returns to rework

#### Scenario: QA evidence is incomplete
- **WHEN** any mandatory test, build, CI, Playwright, artifact, integration, or application service/URL evidence is missing, running, cancelled, unauthorized-skipped, or failing
- **THEN** Sol High keeps the card outside Done and reports the blocker

### Requirement: Sol QA MUST NOT implement code corrections in place
Sol High MUST keep QA independent from implementation and MUST return source-code corrections to the Luna development and review cycle. Sol High retains authorship of OpenSpec corrections, and changes to approved design MUST repeat human Design approval.

#### Scenario: Sol QA finds a bounded code defect
- **WHEN** QA identifies a defect requiring a source-code edit
- **THEN** the workflow returns through Luna implementation, a new Luna review, and a complete Sol QA rerun

### Requirement: Integrated content MUST remain equivalent to reviewed content
Done technical MUST verify that the content integrated in `develop` is equivalent to the reviewed and QA-tested content, or MUST rerun affected review and QA checks when integration changes that content.

#### Scenario: Integration creates a new merge SHA with the same tree
- **WHEN** the `develop` integration SHA differs but preserves the reviewed content tree
- **THEN** Sol High records the equivalence and completes the required integrated application service/URL validation

#### Scenario: Integration changes reviewed content
- **WHEN** the integrated tree differs materially from the reviewed and QA-tested content
- **THEN** the card repeats the affected Code Review and QA checks before Done
