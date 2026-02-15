# Δ backend Specification — dev-indicator-implementation

## ADDED Requirements

### Requirement: Dev may implement new indicators in backend
**Description:** The system SHALL allow the Dev to add new indicators by modifying backend engine code (e.g., ComboStrategy), without touching frontend/interface code.

#### Scenario: Missing indicator is added
- **GIVEN** the Dev needs an indicator not supported (e.g., any pandas_ta indicator)
- **WHEN** the Dev updates the backend engine
- **THEN** the new indicator MUST be available as a column for logic evaluation
- **AND** no frontend/interface files are modified

### Requirement: Indicator additions and corrections must be logged
**Description:** The system MUST log when a new indicator is added or when a backend correction is applied, including the indicator name and column alias.

#### Scenario: Trace records indicator addition
- **GIVEN** a new indicator is implemented
- **WHEN** a run uses that indicator
- **THEN** the trace MUST record the indicator name and alias
- **AND** the log MUST be persisted with the run

#### Scenario: Trace records auto-correction
- **GIVEN** an error was diagnosed and corrected by the Dev
- **WHEN** the backend is updated
- **THEN** the trace MUST record the correction details
- **AND** the log MUST be persisted with the run

### Requirement: Dev must diagnose and fix errors
**Description:** When the system detects an execution error (e.g., missing indicator column), the Dev SHALL diagnose the root cause and apply a backend fix without changing frontend/interface code.

#### Scenario: Missing indicator is diagnosed and fixed
- **GIVEN** a run fails due to an unknown indicator column
- **WHEN** the Dev analyzes the failure
- **THEN** the Dev MUST implement the missing indicator in the backend
- **AND** the run MUST proceed without frontend/interface changes
