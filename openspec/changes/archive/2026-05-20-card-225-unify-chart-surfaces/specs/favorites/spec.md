## ADDED Requirements

### Requirement: Favorites remains chart data base
Favorites result charts SHALL remain driven by the complete result payload available on `/combo/results`.

#### Scenario: Saved result chart opens without extra candle fetch
- **WHEN** a saved favorite result includes candle and marker history
- **THEN** the chart SHALL render from the saved result payload
- **AND** it SHALL NOT require Monitor-specific opportunity data to display the full chart.
