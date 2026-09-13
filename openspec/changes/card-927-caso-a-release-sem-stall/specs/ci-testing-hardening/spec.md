## ADDED Requirements

### Requirement: Long e2e job MUST NOT start when frontend-build failed
The CI job `e2e-playwright` MUST declare a job dependency on `frontend-build`. When `frontend-build` does not succeed, `e2e-playwright` MUST NOT start. A running `e2e-playwright` job MAY keep `timeout-minutes: 30`; that ceiling MUST NOT be used as a substitute for waiting on a failed screen build. This requirement MUST NOT change the native 35-minute CI watcher.

#### Scenario: Screen build failure skips the long e2e job
- **WHEN** `frontend-build` fails
- **THEN** `e2e-playwright` does not start
- **AND** no runner spends the e2e job timeout on that failed build

#### Scenario: Screen build success still runs e2e
- **WHEN** `frontend-build` succeeds and the existing `qa-policy` gate for pull requests also succeeds
- **THEN** `e2e-playwright` may start
