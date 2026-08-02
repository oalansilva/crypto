## ADDED Requirements

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
