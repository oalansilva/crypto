## ADDED Requirements

### Requirement: Daily scanner exposes safe operational diagnostics
The Monitor Telegram alert scanner SHALL expose safe diagnostics that explain whether it can send and why it skipped sending when no message is sent.

#### Scenario: Scanner reports configured destination safely
- **WHEN** a Monitor Telegram alert scan runs
- **THEN** the scan result SHALL include whether alerting is enabled
- **AND** the scan result SHALL include whether a bot token is configured
- **AND** the scan result SHALL include the configured destination chat and thread
- **AND** the scan result SHALL NOT include the bot token value

#### Scenario: Scanner explains no candidate silence
- **WHEN** a Monitor Telegram alert scan finds no catalog opportunities
- **THEN** the scan result SHALL report a skip result with reason `no_opportunities`

#### Scenario: Scanner explains non-sendable statuses
- **WHEN** a Monitor Telegram alert scan sees an opportunity status that is not sendable
- **THEN** the scan result SHALL report the symbol, timeframe, status, and reason `not_sendable`

### Requirement: Daily scanner keeps delivery failures visible
The operational scanner SHALL return a failed process result when Telegram delivery fails.

#### Scenario: Telegram failure returns non-zero from cron script
- **WHEN** the scanner records one or more failed sends
- **THEN** the cron script SHALL print a failure summary without secrets
- **AND** the cron script SHALL exit with non-zero status
