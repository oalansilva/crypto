# ci-testing-hardening Specification

## Purpose
TBD - created by archiving change testing-hardening-ci-e2e. Update Purpose after archive.
## Requirements
### Requirement: Continuous Integration runs on pushes and pull requests
The system MUST provide a GitHub Actions CI workflow that executes automated checks on every push and pull request.

#### Scenario: CI runs on push
- **WHEN** a commit is pushed to the repository
- **THEN** the CI workflow runs and reports a success or failure status

#### Scenario: CI runs on pull request
- **WHEN** a pull request is opened or updated
- **THEN** the CI workflow runs and reports a success or failure status

### Requirement: CI provides actionable artifacts on failures
The CI workflow MUST upload debugging artifacts for failing E2E runs.

#### Scenario: Playwright artifacts uploaded on failure
- **WHEN** an E2E test fails
- **THEN** the workflow uploads at least a Playwright trace and a screenshot (or equivalent artifacts)

### Requirement: Tests are deterministic and do not depend on external market data networks
The automated test suite MUST be able to run without calling external data providers (e.g., Binance/CCXT, Stooq).

#### Scenario: Provider calls are mocked
- **WHEN** backend tests are executed
- **THEN** market data providers are mocked or substituted so no external HTTP/API calls are required

### Requirement: Automated checks cover critical user workflows
The automated suite MUST cover at minimum the Favorites workflow for running a backtest and viewing results.

#### Scenario: Favorites -> View Results works end-to-end
- **WHEN** a user opens Favorites and clicks "View Results" for a favorite strategy
- **THEN** a backtest is executed and the UI navigates to the results screen without errors

### Requirement: Kanban bug E2E tests are discoverable
The Playwright E2E suite SHALL discover and list the Kanban bug regression tests from the standard E2E test directory.

#### Scenario: Playwright lists Kanban bug tests
- **WHEN** `npx playwright test --list` is executed from the frontend package
- **THEN** the output includes the `kanban-bugs.spec.ts` test cases

### Requirement: CI MUST expose a required aggregate QA gate
For pull requests targeting develop, the CI workflow MUST expose a stable `qa-gate` result that succeeds only when all required format, lint, build, backend PostgreSQL tests, coverage, OpenSpec validation, and visual QA jobs have succeeded.

#### Scenario: All required QA jobs succeed
- **WHEN** every required QA job finishes successfully for a pull request to develop
- **THEN** `qa-gate` MUST report success

#### Scenario: A required job fails, cancels, or is unavailable
- **WHEN** any required QA job fails, is cancelled, or does not produce a successful terminal result
- **THEN** `qa-gate` MUST fail

### Requirement: Visual Playwright QA MUST run by default for every delivery
The CI workflow MUST execute the Playwright visual QA job for every delivery candidate regardless of changed path or repository opt-in variables.

#### Scenario: Backend-only change receives visual QA
- **WHEN** a pull request changes backend, workflow, documentation, or another area outside frontend
- **THEN** the Playwright visual QA job MUST still execute the critical visual regression suite

#### Scenario: UI change receives targeted visual QA
- **WHEN** a pull request changes a user-facing screen or component
- **THEN** the Playwright visual QA suite MUST include the affected screen at configured desktop and mobile viewports

### Requirement: Functional Playwright QA MUST provide a reliable gate signal
The existing functional Playwright suite MUST remain executable in the same CI job. Stale selectors, duplicated test IDs, and fixtures that no longer match the rendered product MUST be corrected before the suite becomes a required dependency of `qa-gate`.

#### Scenario: Existing functional test observes a changed product surface
- **WHEN** an existing functional test fails because its locator, fixture, or expected UI state is obsolete
- **THEN** the test MUST be updated to assert the intended current product contract without weakening the underlying coverage

### Requirement: Visual QA opt-out MUST be explicitly authorized and auditable
The Playwright visual job MAY bypass test execution only when the linked card has both the `qa-visual-skip` label and an explicit authorized Alan comment documenting the reason. An implicit path filter, repository variable, or label alone MUST NOT bypass visual QA.

#### Scenario: Authorized visual QA dispensation
- **WHEN** the linked card contains the required label and a qualifying Alan comment
- **THEN** the visual QA job MUST record the dispensation reason and finish successfully without running visual tests

#### Scenario: Unauthorized visual QA skip attempt
- **WHEN** the linked card has only the label, only a comment, an unauthorized commenter, or no linked card
- **THEN** the visual QA job MUST fail or execute the required visual tests; it MUST NOT silently skip

### Requirement: Visual QA failures MUST retain diagnostic artifacts
The CI workflow MUST publish Playwright report, trace, screenshot diff, and video/test-result artifacts when visual QA fails.

#### Scenario: Visual regression mismatch
- **WHEN** a Playwright visual assertion fails
- **THEN** the workflow MUST upload the diagnostic artifacts needed to inspect expected, actual, and diff output
