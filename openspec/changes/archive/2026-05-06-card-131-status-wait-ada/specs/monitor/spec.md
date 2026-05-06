## ADDED Requirements

### Requirement: Monitor list uses strategy decision timeframe
The Monitor list SHALL group opportunities into HOLD, WAIT, and EXIT using the backend opportunity decision state for the strategy timeframe. Card price timeframe preferences MUST NOT downgrade a list row from HOLD or EXIT to WAIT.

#### Scenario: Strategy timeframe differs from price card timeframe
- **WHEN** an opportunity has `is_holding=true` and a HOLD-compatible status such as `HOLDING` or `EXIT_NEAR`
- **AND** the saved card price timeframe differs from the opportunity strategy timeframe
- **THEN** the Monitor list MUST still place that opportunity in HOLD
- **AND** timeframe mismatch review MUST remain limited to the chart modal display context.
