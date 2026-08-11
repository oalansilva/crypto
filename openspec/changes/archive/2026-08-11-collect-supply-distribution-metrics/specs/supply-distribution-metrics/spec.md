## ADDED Requirements

### Requirement: Supply distribution is collected from Glassnode
The system SHALL collect supply distribution for supported assets through the existing Glassnode connector using daily entity supply-band metrics and long-term holder supply.

#### Scenario: Supply distribution requested
- **WHEN** supply distribution is requested for `BTC`
- **THEN** the system SHALL fetch entity supply bands from `supply_balance_less_0001`, `supply_balance_0001_001`, `supply_balance_001_01`, `supply_balance_01_1`, `supply_balance_1_10`, `supply_balance_10_100`, `supply_balance_100_1k`, `supply_balance_1k_10k`, `supply_balance_10k_100k`, and `supply_balance_more_100k`
- **AND** long-term holder supply from `lth_sum`.

#### Scenario: Unsupported basis rejected
- **WHEN** supply distribution is requested with a basis other than `entity`
- **THEN** the system SHALL reject the request before calling Glassnode.

### Requirement: Supply dashboard payload exposes wallet bands
The system SHALL expose dashboard-ready supply bands with latest value, previous window value, absolute change, percentage change, and share of represented supply.

#### Scenario: Numeric band series available
- **GIVEN** a supply band contains at least two numeric points in the selected window
- **WHEN** the system aggregates the band
- **THEN** the band payload SHALL include latest supply, previous supply, absolute change, percentage change, and share percentage.

#### Scenario: Sparse band series remains valid
- **GIVEN** a supply band contains fewer than two numeric points
- **WHEN** the system aggregates the band
- **THEN** the band payload SHALL remain present
- **AND** unavailable derived fields SHALL be `null`.

### Requirement: Supply cohorts are aggregated
The system SHALL aggregate supply cohorts for shrimps, whales, and hodlers.

#### Scenario: Shrimp and whale cohorts calculated
- **WHEN** supply bands are aggregated
- **THEN** `shrimps` SHALL include entity bands with balance below `1 BTC`
- **AND** `whales` SHALL include entity bands with balance greater than or equal to `1000 BTC`.

#### Scenario: Hodler cohort calculated
- **WHEN** long-term holder supply is returned by Glassnode
- **THEN** `hodlers` SHALL include latest, previous, absolute change, and percentage change from the fetched `lth_sum` series.

### Requirement: Whale movement and alerts are detected
The system SHALL detect whale movement as the windowed change in aggregate supply held by entities with balance greater than or equal to `1000 BTC`.

#### Scenario: Whale accumulation alert emitted
- **GIVEN** whale supply increases by at least `1000 BTC` over the selected window
- **WHEN** the system aggregates supply distribution
- **THEN** the response SHALL include a `whale-alert` alert
- **AND** `whale_movement.direction` SHALL be `accumulation`.

#### Scenario: Whale distribution alert emitted
- **GIVEN** whale supply decreases by at least `1000 BTC` over the selected window
- **WHEN** the system aggregates supply distribution
- **THEN** the response SHALL include a `whale-alert` alert
- **AND** `whale_movement.direction` SHALL be `distribution`.

#### Scenario: Movement below threshold is not an alert
- **GIVEN** whale supply changes by less than `1000 BTC` over the selected window
- **WHEN** the system aggregates supply distribution
- **THEN** the response SHALL NOT include a `whale-alert` alert.

### Requirement: Supply distribution is exposed through API
The system SHALL expose supply distribution through the on-chain Glassnode API surface.

#### Scenario: API returns supply distribution payload
- **WHEN** `GET /api/onchain/glassnode/BTC/supply-distribution?basis=entity&window=7d` is requested
- **THEN** the API SHALL return asset, basis, window, interval, cached status, bands, cohorts, whale movement, alerts, and source metadata.

#### Scenario: Provider errors are mapped
- **WHEN** the supply distribution service raises configuration, validation, or rate-limit errors
- **THEN** the API SHALL map them to the same HTTP statuses used by the existing Glassnode routes.

### Requirement: Supply distribution dashboard is available
The system SHALL provide a protected frontend dashboard for supply distribution.

#### Scenario: Dashboard renders wallet bands
- **WHEN** a user opens `/supply-distribution`
- **THEN** the dashboard SHALL request supply distribution from the backend
- **AND** display wallet/entity bands, shrimp/whale/hodler cohorts, whale movement, and alert state.

#### Scenario: Dashboard window changes
- **WHEN** a user selects `24h`, `7d`, or `30d`
- **THEN** the dashboard SHALL refresh the backend request with the selected window.
