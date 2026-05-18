## MODIFIED Requirements

### Requirement: Monitor graph shares chart base
Monitor graph modal SHALL use the same chart base as Favorites while retaining Monitor-specific operational context.

#### Scenario: Monitor keeps signal context
- **WHEN** the Monitor graph modal opens
- **THEN** it SHALL show the shared candle/volume chart
- **AND** it SHALL keep signal badge, strategy summary, timeframe selector, signal context, signal history, risk/stop details, parameters and notes according to the opportunity visibility rules.
