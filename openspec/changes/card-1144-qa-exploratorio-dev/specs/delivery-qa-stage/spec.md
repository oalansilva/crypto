## MODIFIED Requirements

### Requirement: QA MUST gate Done technical
A card MUST NOT move to Done until required QA checks have reached a terminal successful result, the work is integrated in develop, and the documented runtime reconciliation has completed. With overlay `qa_dev.enabled` true, the card MUST also have a DEV test report for the integrated code, and that report MUST NOT carry a failed criterion. A report with no passed criterion, or taken with DEV or a continuous service down, MUST keep the card outside Done until Alan decides.

#### Scenario: QA checks are still running or failing
- **WHEN** any required QA check is running, cancelled, skipped without an authorized dispensation, or failing
- **THEN** the card MUST remain outside Done and report the blocking evidence

#### Scenario: QA and runtime evidence are complete
- **WHEN** QA is green, the reviewed work is integrated in develop, `./restart` has completed, and the system URL serves the new result
- **THEN** the card MAY move to Done technical with the corresponding evidence, once the DEV test report required by `qa_dev` allows it

#### Scenario: Failed DEV test keeps the card out of Done
- **WHEN** `qa_dev` is on and the DEV test report has a failed criterion
- **THEN** the card MUST remain outside Done
- **AND** it MUST follow `QA → In Progress → Code Review → QA` until the correction is in DEV and the criterion passes, unless a retest without diff, after Alan disagrees, clears the criterion

#### Scenario: Inconclusive DEV test keeps the card out of Done
- **WHEN** `qa_dev` is on and the DEV test report is `INCONCLUSIVO`
- **THEN** the card MUST remain in QA
- **AND** it MAY move to Done only after a new report allows it or Alan's exact release comment
