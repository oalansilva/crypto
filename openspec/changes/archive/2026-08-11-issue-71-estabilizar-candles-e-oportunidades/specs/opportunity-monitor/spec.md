## MODIFIED Requirements

### Requirement: Opportunity Monitor tolerates partial data-source failures
The opportunity monitor computation SHALL always preserve successful strategy cards even when another strategy or data-source job fails (timeout, invalid symbol payload, provider timeout, temporary network failure).
Failures MUST be represented as skipped processing entries for that strategy, and the endpoint MUST continue returning the remaining valid opportunities.

#### Scenario: Slow data source does not block all opportunities
- **WHEN** one strategy data fetch exceeds timeout or fails
- **THEN** the endpoint returns available opportunities for other strategies in `200`.
- **AND** the failed strategy is omitted with failure recorded for diagnostics.

#### Scenario: Invalid or unsupported strategy source does not fail full monitor update
- **WHEN** a single strategy has an invalid data source/configuration during resolution
- **THEN** the endpoint returns `200`.
- **AND** valid strategies continue to be computed.

### Requirement: Simplified Hold Status Display
**Description:** The system SHALL display a clear binary indicator: HOLD (active position) or WAIT (no position). When holding, show distance to exit; when not holding, show distance to entry.

#### Scenario: HOLD distance shown
- **WHEN** the strategy is in HOLD status
- **THEN** the UI displays distance to exit

#### Scenario: WAIT distance shown
- **WHEN** the strategy is in WAIT status
- **THEN** the UI displays distance to entry
