## MODIFIED Requirements

### Requirement: Favorites result chart markers use current Monitor signal history
Result charts opened from Favorites SHALL prefer Monitor `signal_history` over saved favorite trade history for entry and exit markers when current Monitor history is available.

#### Scenario: Marker dates align with Monitor
- **WHEN** Favorites opens a result chart for a favorite also present in Monitor
- **AND** Monitor returns current signal history
- **THEN** the chart marker timestamps are derived from Monitor signal history
- **AND** stale saved trade marker timestamps are not rendered
