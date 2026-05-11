## ADDED Requirements

### Requirement: Monitor Telegram scan tracks observed status
The Monitor Telegram scan SHALL persist the latest observed status for each catalog `symbol + timeframe` independently from sent alert history.

#### Scenario: First observed sendable status can alert
- **WHEN** no observed status exists for a catalog `symbol + timeframe`
- **AND** the current Monitor status is sendable
- **THEN** the scan SHALL treat it as a new alert candidate
- **AND** persist the current status as the latest observed status

#### Scenario: Unchanged observed status does not alert
- **WHEN** the latest observed status for a `symbol + timeframe` equals the current Monitor status
- **THEN** the scan SHALL NOT send another alert for that unchanged status
- **AND** SHALL update the observed timestamp

#### Scenario: Silent status transition into sendable status alerts
- **WHEN** the latest observed status for a `symbol + timeframe` is not sendable
- **AND** the current Monitor status changes to a sendable status
- **THEN** the scan SHALL send an alert candidate using the observed previous status
- **AND** persist the current status as latest observed status

#### Scenario: Non-sendable status still updates observation
- **WHEN** the current Monitor status is not sendable
- **THEN** the scan SHALL persist that status as latest observed status
- **AND** SHALL NOT create an alert candidate
