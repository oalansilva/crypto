## ADDED Requirements

### Requirement: Mining metrics are collected from Glassnode
The system SHALL collect mining network metrics for supported assets through the existing Glassnode connector.

#### Scenario: Mining metrics requested
- **WHEN** mining network metrics are requested for `BTC`
- **THEN** the system SHALL fetch hash rate from `hash_rate_mean`
- **AND** difficulty from `difficulty_latest`
- **AND** total miner revenue from `revenue_sum`.

### Requirement: Mining metrics expose moving averages
The system SHALL calculate trailing 7d and 30d moving averages for each numeric daily mining metric series.

#### Scenario: Full windows available
- **GIVEN** a mining metric series contains at least 30 numeric daily points
- **WHEN** the system enriches the series
- **THEN** the latest point SHALL include `ma_7d`
- **AND** `ma_30d`.

#### Scenario: Insufficient windows available
- **GIVEN** a mining metric series contains fewer than 7 numeric daily points
- **WHEN** the system enriches the series
- **THEN** moving average fields SHALL remain absent for those points
- **AND** the response SHALL still be valid.

#### Scenario: Non-daily interval rejected
- **WHEN** mining network metrics are requested with an interval other than `24h`
- **THEN** the system SHALL reject the request before calling Glassnode.

### Requirement: Mining metrics track ATH
The system SHALL track the all-time-high value within the fetched mining metric series.

#### Scenario: ATH calculated
- **GIVEN** a mining metric series contains numeric points
- **WHEN** the system enriches the series
- **THEN** the response SHALL include the maximum value and timestamp observed in that fetched series.

### Requirement: Mining metrics alert on sharp drops
The system SHALL emit a `sharp_drop` alert when the latest numeric value falls more than 10% below its 7d moving average.

#### Scenario: Sharp drop detected
- **GIVEN** a mining metric latest value is less than 90% of its 7d moving average
- **WHEN** the system enriches the series
- **THEN** the metric response SHALL include a `sharp_drop` alert
- **AND** include the drop percentage versus the 7d moving average.

#### Scenario: Boundary is not an alert
- **GIVEN** a mining metric latest value is exactly 90% of its 7d moving average
- **WHEN** the system enriches the series
- **THEN** the metric response SHALL NOT include a `sharp_drop` alert.

### Requirement: Mining metrics are exposed through API
The system SHALL expose mining network metrics through the on-chain Glassnode API surface.

#### Scenario: API returns mining metric payload
- **WHEN** `GET /api/onchain/glassnode/BTC/mining-metrics` is requested
- **THEN** the API SHALL return asset, interval, cached status, metric summaries, enriched points, ATH data, and alerts.

#### Scenario: Provider errors are mapped
- **WHEN** the mining metric service raises configuration, validation, or rate-limit errors
- **THEN** the API SHALL map them to the same HTTP statuses used by the existing Glassnode routes.
