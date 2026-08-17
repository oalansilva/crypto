## ADDED Requirements

### Requirement: Code Review evidence MUST include the native Bugbot result
QA handoff and Done technical evidence SHALL include the `/review-bugbot` outcome for the reviewed SHA, in addition to the existing QA checks, visual artifacts and next action.

#### Scenario: QA handoff cites Bugbot
- **WHEN** QA or Done evidence is published
- **THEN** the summary MUST include the `/review-bugbot` result (findings, no findings, classified residuals, or spawn-failed plus fallback)

### Requirement: GitHub Bugbot is a QA complement, not the pre-commit Code Review
Automatic Bugbot on the pull request to `develop` MAY run as part of QA. It MUST NOT replace the pre-commit `/review-bugbot` on uncommitted changes. Incremental Review SHOULD be enabled so later QA pushes do not re-review the whole PR by default.

#### Scenario: PR Bugbot does not skip local Code Review
- **WHEN** a pull request to `develop` is opened after a local `/review-bugbot` run
- **THEN** the local pre-commit review remains the Code Review gate
- **AND** the remote Bugbot MAY skip a duplicate patch via patch ID without waiving the local gate

### Requirement: Autofix MUST NOT commit to the existing PR branch
Bugbot Autofix MUST remain Off for this repository, or at most create a new branch. Autofix MUST NOT commit onto the existing reviewed branch. Agent Review MUST NOT run automatically after every commit.

#### Scenario: Autofix on existing branch is forbidden
- **WHEN** Bugbot reports findings on a pull request
- **THEN** a Cloud Agent MUST NOT push fixes to the existing PR branch as Autofix
- **AND** Agent Review automatic-after-commit MUST remain disabled
