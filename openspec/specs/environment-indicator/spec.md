## Purpose

Ensure authenticated users can always identify whether they are using the development or production environment.

## Requirements

### Requirement: Authenticated environment indicator

The system SHALL display a persistent environment indicator on every authenticated application screen.

#### Scenario: Protected desktop route shows environment
- **WHEN** an authenticated user opens a protected desktop route such as `/monitor`
- **THEN** the shared application shell displays an environment indicator without requiring page-specific UI

#### Scenario: Protected mobile route shows environment
- **WHEN** an authenticated user opens a protected route on a mobile viewport
- **THEN** the fixed mobile shell displays an environment indicator before opening the navigation drawer

### Requirement: Environment label resolution

The system SHALL resolve the displayed environment from centralized frontend runtime/build configuration and SHALL label it as `DEV` or `PROD`.

#### Scenario: Development environment
- **WHEN** the frontend is running with `VITE_APP_ENV=development`, `VITE_APP_ENV=dev`, or Vite development mode
- **THEN** the environment indicator displays `DEV`

#### Scenario: Production environment
- **WHEN** the frontend is running with `VITE_APP_ENV=production`, `VITE_APP_ENV=prod`, or Vite production mode
- **THEN** the environment indicator displays `PROD`

#### Scenario: Develop restart build
- **WHEN** the local restart flow builds the frontend from a non-main branch without an explicit environment override
- **THEN** the build receives a development environment label and the indicator displays `DEV`

#### Scenario: Main restart build
- **WHEN** the local restart flow builds the frontend from the `main` branch without an explicit environment override
- **THEN** the build receives a production environment label and the indicator displays `PROD`

### Requirement: Distinct visual treatment

The system SHALL use distinct visual treatments for development and production environment indicators while preserving the existing design system.

#### Scenario: Development visual state
- **WHEN** the resolved environment is development
- **THEN** the indicator uses an unmistakable development visual state based on existing dark-shell tokens and yellow warning emphasis

#### Scenario: Production visual state
- **WHEN** the resolved environment is production
- **THEN** the indicator uses a clear but calmer production visual state that does not dominate normal operation
