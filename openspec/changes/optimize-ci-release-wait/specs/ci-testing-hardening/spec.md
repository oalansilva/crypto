## MODIFIED Requirements

### Requirement: Continuous Integration runs on pushes and pull requests
The system MUST provide a GitHub Actions CI workflow that executes automated checks on pushes to `develop` and `main` and on pull requests targeting those branches. A temporary branch with a pull request MUST NOT execute equivalent full suites for both its branch push and pull-request event.

#### Scenario: CI runs on integration or production push
- **WHEN** a commit is pushed to `develop` or `main`
- **THEN** the CI workflow runs and reports a success or failure status

#### Scenario: CI runs on pull request
- **WHEN** a pull request targeting `develop` or `main` is opened or updated
- **THEN** the CI workflow runs and reports a success or failure status

#### Scenario: Temporary branch is pushed before its pull request
- **WHEN** a commit is pushed to a temporary card, change, or release branch
- **THEN** the workflow does not launch a duplicate full push suite and validation occurs through the pull-request event

## ADDED Requirements

### Requirement: Independent required QA jobs MUST run concurrently
The CI workflow MUST allow independent required jobs to start without an artificial dependency while retaining their successful terminal results as dependencies of `qa-gate`.

#### Scenario: Backend and browser suites validate a pull request
- **WHEN** a pull-request CI run starts and the Playwright job does not consume artifacts from backend integration tests
- **THEN** Playwright and backend integration tests may run concurrently and `qa-gate` waits for both

#### Scenario: Concurrent required job fails
- **WHEN** either Playwright or backend integration tests fails after running concurrently
- **THEN** `qa-gate` fails and the pull request remains blocked
