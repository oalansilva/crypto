## ADDED Requirements

### Requirement: General scanner preserves daily curated scope
Monitor Telegram daily scans SHALL continue to evaluate the curated Monitor catalog using configured tier scope and SHALL NOT increase schedule cadence as part of delivery diagnostics.

#### Scenario: Daily scan keeps tier-filtered catalog source
- **WHEN** the daily Monitor Telegram scanner runs
- **THEN** it SHALL evaluate the curated catalog source with the configured tier filter
- **AND** it SHALL preserve the existing daily cadence decision outside application code
