## ADDED Requirements

### Requirement: Favorites screen is covered by E2E tests
The system MUST provide E2E tests that validate the Favorites screen core workflow.

#### Scenario: Favorites loads successfully
- **WHEN** the E2E test opens the Favorites route
- **THEN** the Favorites list renders without client-side errors

#### Scenario: View Results triggers backtest and navigates to results
- **WHEN** the E2E test clicks the "View Results" action for a favorite
- **THEN** the UI triggers a backtest request and navigates to the results page
