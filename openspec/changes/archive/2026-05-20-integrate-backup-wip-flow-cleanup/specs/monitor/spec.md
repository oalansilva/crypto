## ADDED Requirements

### Requirement: Monitor chart opens with stable operational timeframe
Monitor opportunity cards SHALL open charts using the validated `1d` operational timeframe from the saved WIP.

#### Scenario: User opens a Monitor chart
- **WHEN** the user opens chart analysis from a Monitor opportunity card
- **THEN** the chart request uses timeframe `1d` and does not expose stale intraday timeframe controls
