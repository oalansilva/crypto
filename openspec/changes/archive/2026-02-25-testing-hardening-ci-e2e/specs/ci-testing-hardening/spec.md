## ADDED Requirements

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
