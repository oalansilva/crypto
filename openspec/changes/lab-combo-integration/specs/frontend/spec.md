## ADDED Requirements

### Requirement: Combo Optimization Summary in Lab Run UI
**Description:** The system SHALL render a dedicated Combo optimization summary block in the Lab run page for every user that opens the run.

#### Scenario: User views Combo optimization status
Given a user opens `/lab/runs/:runId`  
When the run contains Combo optimization data  
Then the UI MUST show optimization status, template reference, and execution timestamp in a visible section

### Requirement: Visibility of Applied Parameters and Limits
**Description:** The system MUST display the applied best parameters and the optimization limits snapshot sourced from the run payload.

#### Scenario: User inspects applied Combo parameters
Given Combo optimization finished successfully for the run  
When the user expands optimization details  
Then the UI MUST list best parameter key/value pairs and MUST show the limits snapshot used in that optimization

### Requirement: Final Result Context After Automatic Application
**Description:** The system SHALL indicate that the displayed final backtest is post-Combo parameter application and is the artifact for Trader final validation.

#### Scenario: User distinguishes pre and post Combo context
Given the run reached final backtest after Combo optimization  
When backtest metrics are presented in the Lab run page  
Then the UI MUST label the result as final post-Combo output and MUST avoid implying a manual parameter-approval step

### Requirement: Combo Failure Transparency
**Description:** The system SHALL expose Combo optimization failure state in the Lab UI when the backend persists an error for that stage.

#### Scenario: Optimization error is visible
Given Combo optimization fails during a Lab run  
When the run page is rendered  
Then the UI MUST show failed status with the persisted error summary and MUST keep the section visible for debugging
