## ADDED Requirements

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
