# monitor-telegram-alerts Specification

## Purpose
Internal Monitor Telegram alerting for curated Monitor opportunities.

## Requirements
### Requirement: Internal Monitor Telegram alerts
The system SHALL generate internal Telegram alert drafts from Monitor opportunities and SHALL send them only to an allowlisted internal Telegram destination when alerting is enabled and fully configured.

#### Scenario: Enabled alert sends to allowlisted internal destination
- **WHEN** Monitor Telegram alerts are enabled with a bot token and an allowlisted internal chat destination
- **AND** a relevant Monitor opportunity changes to a sendable status
- **THEN** the system SHALL send a standardized internal alert message to the configured internal destination
- **AND** the message SHALL include symbol, timeframe, previous reading, new reading, severity, context, and educational disclaimer
- **AND** the message SHALL include text Alan can review or adapt before sending externally

#### Scenario: External beta group is not targeted
- **WHEN** the system sends a Monitor Telegram alert
- **THEN** it SHALL use only the configured internal allowlisted destination
- **AND** it SHALL NOT send directly to the beta testers group

#### Scenario: Missing configuration uses dry run
- **WHEN** Monitor Telegram alerts are enabled but bot token or destination is missing
- **THEN** the system SHALL NOT call Telegram
- **AND** it SHALL record the candidate alert as a dry run result

### Requirement: Alert anti-noise controls
The system SHALL prevent repeated or excessive internal Telegram alerts through deduplication and rate limiting.

#### Scenario: Duplicate status inside minimum window is skipped
- **WHEN** an alert for the same symbol, timeframe, and status was already recorded inside the configured minimum repeat window
- **THEN** the system SHALL skip sending a duplicate alert
- **AND** it SHALL record or report the skip reason as duplicate

#### Scenario: Rate limit caps messages per window
- **WHEN** the configured maximum alert count for the current rate-limit window has already been reached
- **THEN** the system SHALL skip additional sends
- **AND** it SHALL report the skip reason as rate limited

### Requirement: Alert audit trail
The system SHALL persist an audit trail for every sent or dry-run Monitor Telegram alert attempt.

#### Scenario: Alert attempt is audited
- **WHEN** the system processes a sendable Monitor opportunity alert
- **THEN** it SHALL persist alert timestamp, symbol, timeframe, previous status, new status, severity, destination, send result, payload hash, and source
- **AND** the audit row SHALL be usable for later deduplication

#### Scenario: Telegram send failure is audited
- **WHEN** Telegram delivery fails
- **THEN** the system SHALL record the failure status and error text
- **AND** it SHALL NOT raise an unhandled exception that stops processing other candidate alerts

### Requirement: Administrative execution path
The system SHALL provide an admin-only backend execution path to run a Monitor Telegram alert scan manually.

#### Scenario: Admin triggers scan
- **WHEN** an authenticated admin calls the alert scan endpoint
- **THEN** the system SHALL run one Monitor alert scan
- **AND** return counts for candidates, sent, dry-run, duplicates, rate-limited, skipped, and failed alerts

#### Scenario: Non-admin cannot trigger scan
- **WHEN** a non-admin user calls the alert scan endpoint
- **THEN** the system SHALL reject the request using the existing admin authentication dependency
