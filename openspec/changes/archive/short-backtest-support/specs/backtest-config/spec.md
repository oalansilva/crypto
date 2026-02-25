## ADDED Requirements

### Requirement: Backtest direction parameter in configuration
The system SHALL accept an optional **direction** parameter in the backtest (and optimization) configuration. The parameter SHALL have values `"long"` or `"short"`. The default SHALL be `"long"`. The parameter SHALL be exposed in the UI on the Configure Backtest screen and SHALL be sent in backtest, optimization and batch backtest request payloads.

#### Scenario: User selects direction on Configure Backtest screen
- **GIVEN** the user is on the Configure Backtest screen (ComboConfigurePage)
- **WHEN** the user views the configuration form
- **THEN** the UI MUST display a control (e.g. dropdown or toggle) for **Direction** with options **Long** and **Short**
- **AND** the default selected value MUST be **Long**
- **AND** the selected value MUST be included in the payload when the user runs backtest or batch backtest

#### Scenario: Backend receives direction in backtest request
- **GIVEN** a client sends a backtest request to the API (e.g. POST /api/combos/backtest or equivalent)
- **WHEN** the request body includes `"direction": "short"`
- **THEN** the backend MUST run the backtest in short mode (interpret signal 1 as open short, -1 as close short; apply short PnL/stop/take-profit)
- **AND** when the request omits `direction` or sends `"direction": "long"`, the backend MUST run in long mode (current behavior)

#### Scenario: Optimization and batch payloads accept direction
- **GIVEN** the user triggers parameter optimization or a batch backtest
- **WHEN** the request payload includes `"direction": "short"`
- **THEN** each backtest run within the optimization or batch MUST use short mode
- **AND** when the payload omits `direction` or sends `"direction": "long"`, all runs MUST use long mode
