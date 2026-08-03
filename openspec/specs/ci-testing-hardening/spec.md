# ci-testing-hardening Specification

## Purpose
TBD - created by archiving change testing-hardening-ci-e2e. Update Purpose after archive.
## Requirements
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

### Requirement: Independent required QA jobs MUST run concurrently
The CI workflow MUST allow independent required jobs to start without an artificial dependency while retaining their successful terminal results as dependencies of `qa-gate`.

#### Scenario: Backend and browser suites validate a pull request
- **WHEN** a pull-request CI run starts and the Playwright job does not consume artifacts from backend integration tests
- **THEN** Playwright and backend integration tests may run concurrently and `qa-gate` waits for both

#### Scenario: Concurrent required job fails
- **WHEN** either Playwright or backend integration tests fails after running concurrently
- **THEN** `qa-gate` fails and the pull request remains blocked

### Requirement: Backend unit-test decisions MUST be auditable
The repository MUST maintain a reproducible inventory of every backend unit-test file with its protected production behavior, current reachability, persistence need, regression risk, decision to keep, refactor/consolidate, or remove, and supporting evidence. A test MUST NOT be removed solely because it is slow, old, rarely used, or named for removed/coverage behavior.

#### Scenario: Every discovered unit-test file is classified
- **WHEN** the audit validator compares the inventory with `backend/tests/unit/test_*.py`
- **THEN** every discovered file has exactly one decision and the inventory contains no stale file entry

#### Scenario: A test file is proposed for removal
- **WHEN** the audit classifies a file as remove
- **THEN** its evidence proves that the production behavior is unreachable or removed, or that equivalent regression coverage remains elsewhere

### Requirement: Backend unit-test performance MUST be measured reproducibly
The backend unit-test workflow MUST produce comparable measurements that include revision/environment, collected cases, total duration, per-file duration aggregation, p95, the ten slowest files, skips, and warning counts.

#### Scenario: A baseline or optimized measurement is recorded
- **WHEN** the documented benchmark command runs against the backend unit suite with PostgreSQL and coverage enabled
- **THEN** it emits machine-readable raw evidence and a deterministic summary containing all required metrics

### Requirement: Pure unit tests MUST NOT pay PostgreSQL reset cost
Tests that do not exercise persistence MUST run without creating application/workflow schemas, opening a PostgreSQL engine, or truncating database tables. Tests that exercise persistence MUST explicitly request isolated PostgreSQL state and MUST retain safeguards against runtime database names.

#### Scenario: A pure test runs
- **WHEN** a unit test without the persistence marker or fixture executes
- **THEN** the shared database-isolation helper performs no engine, schema, or truncate operation

#### Scenario: A persistence test runs
- **WHEN** a marked backend unit test exercises application or workflow persistence
- **THEN** it uses PostgreSQL, validates the dedicated test database name, prepares required schemas, and resets state deterministically

### Requirement: Backend unit tests MUST use a bounded low-overhead runner
The CI workflow MUST avoid starting pytest and coverage once per unit-test file while preserving actionable progress, per-test hang protection, a job-level timeout, failure reporting, and coverage artifact compatibility.

#### Scenario: The backend unit suite runs in CI
- **WHEN** the `backend-unit-tests` job executes
- **THEN** it runs the unit directory in a consolidated bounded coverage session and uploads coverage plus timing evidence

#### Scenario: A test hangs or fails
- **WHEN** a case exceeds its timeout or an assertion fails
- **THEN** the job terminates with a non-success result and identifies the affected test in its logs or report

### Requirement: Optimization MUST preserve regression protection
The optimized backend test workflow MUST keep total backend line coverage and differential coverage at 70% or higher, MUST run unit and integration tests against PostgreSQL, and MUST classify persistent skips and recurring warnings without silently suppressing project failures.

#### Scenario: Optimized tests reach QA
- **WHEN** the reviewed change is validated
- **THEN** unit tests, integration tests, total coverage, differential coverage, and required QA jobs reach successful terminal results with thresholds unchanged or improved

#### Scenario: A persistent skip or warning remains
- **WHEN** the optimized suite reports a repeated skip or warning category
- **THEN** the audit records its cause and disposition, and any suppression is limited to understood non-project noise

### Requirement: Optimization outcome MUST be demonstrated statistically
The implementation MUST compare at least three comparable optimized runs with the five green reference runs. The optimized median MUST improve by at least 30%, or the evidence MUST prove that the measured bottleneck is outside the suite and link a specific follow-up action.

#### Scenario: Performance target is met
- **WHEN** three comparable optimized runs complete
- **THEN** their median `backend-unit-tests` duration is at least 30% lower than the reference median and the evidence records the runs and calculation

#### Scenario: Performance target is not met
- **WHEN** the optimized median improves by less than 30%
- **THEN** the card remains incomplete unless evidence isolates the external bottleneck and a specific tracked follow-up is created
