## ADDED Requirements

### Requirement: Combo Optimization Summary in Lab Run UI
**Description:** The system SHALL render a dedicated Combo optimization summary block in the Lab run page for every user that opens the run.

#### Scenario: User views Combo optimization status
- **GIVEN** a user opens `/lab/runs/:runId`
- **WHEN** the run contains Combo optimization data
- **THEN** the UI MUST show optimization status, template reference, and execution timestamp in a visible section
- **AND** the optimization summary section MUST remain visible in the run page

### Requirement: Visibility of Applied Parameters and Limits
**Description:** The system MUST display the applied best parameters and the optimization limits snapshot sourced from the run payload.

#### Scenario: User inspects applied Combo parameters
- **GIVEN** Combo optimization finished successfully for the run
- **WHEN** the user expands optimization details
- **THEN** the UI MUST list best parameter key/value pairs
- **AND** the UI MUST show the limits snapshot used in that optimization

### Requirement: Final Result Context After Automatic Application
**Description:** The system SHALL indicate that the displayed final backtest is post-Combo parameter application and is the artifact for Trader final validation.

#### Scenario: User distinguishes pre and post Combo context
- **GIVEN** the run reached final backtest after Combo optimization
- **WHEN** backtest metrics are presented in the Lab run page
- **THEN** the UI MUST label the result as final post-Combo output
- **AND** the UI MUST avoid implying a manual parameter-approval step

#### Scenario: Final Result Context After Automatic Application
- **GIVEN** Combo best parameters were automatically applied before the final backtest
- **WHEN** the user reviews final result context in the Lab run page
- **THEN** the UI MUST indicate the displayed final result reflects automatically applied Combo parameters
- **AND** the UI MUST indicate this artifact is used for Trader final validation

### Requirement: Combo Failure Transparency
**Description:** The system SHALL expose Combo optimization failure state in the Lab UI when the backend persists an error for that stage.

#### Scenario: Optimization error is visible
- **GIVEN** Combo optimization fails during a Lab run
- **WHEN** the run page is rendered
- **THEN** the UI MUST show failed status with the persisted error summary
- **AND** the optimization section MUST remain visible for debugging
