## ADDED Requirements

### Requirement: Exchange flows include inflow and outflow
The system SHALL collect exchange inflow and outflow volumes for supported assets.

#### Scenario: Inflow and outflow collected
- **WHEN** exchange flows are requested for an asset
- **THEN** the system SHALL fetch inflow from `transfers_volume_to_exchanges_sum`
- **AND** outflow from `transfers_volume_from_exchanges_sum`.

### Requirement: Exchange flows include netflow
The system SHALL collect or derive netflow for exchange flows.

#### Scenario: Netflow collected
- **WHEN** exchange flows are requested for an asset
- **THEN** the system SHALL fetch netflow from `transfers_volume_exchanges_net`.

#### Scenario: Per-exchange netflow fallback
- **GIVEN** per-exchange inflow and outflow exist
- **AND** per-exchange netflow is missing for an exchange
- **WHEN** exchange flows are aggregated
- **THEN** netflow for that exchange SHALL equal `inflow - outflow`.

### Requirement: Exchange flows aggregate by exchange and total
The system SHALL return exchange flow aggregation by exchange and total.

#### Scenario: Object payload aggregates exchanges
- **GIVEN** Glassnode returns object values keyed by exchange
- **WHEN** the system aggregates the window
- **THEN** each exchange SHALL have inflow, outflow, and netflow totals
- **AND** the response SHALL include overall totals.

#### Scenario: Scalar payload aggregates total
- **GIVEN** Glassnode returns scalar values
- **WHEN** the system aggregates the window
- **THEN** the scalar values SHALL be aggregated into the overall total.

### Requirement: Exchange flows support operational windows
The system SHALL support `24h`, `7d`, and `30d` windows.

#### Scenario: Supported window requested
- **WHEN** `window=7d` is requested
- **THEN** the service SHALL request data from the last seven days.

#### Scenario: Unsupported window rejected
- **WHEN** an unsupported window is requested
- **THEN** the API SHALL return a validation error.
