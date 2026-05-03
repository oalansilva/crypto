## ADDED Requirements

### Requirement: Monitor removes highlighted visual noise
The Monitor screen SHALL remove the visual elements highlighted in card 116 while preserving the primary trading workflow.

#### Scenario: User opens Monitor
- **WHEN** the user opens the Monitor
- **THEN** the page does not show `Binance system`
- **AND** the Monitor toolbar does not show `Binance · live`
- **AND** the filter bar does not show sort buttons `Risco` or `Par`
- **AND** the signal table has a single `Status` column
- **AND** the signal row actions do not show a `Mais` button

#### Scenario: Primary row actions remain available
- **WHEN** the user opens the Monitor
- **THEN** row actions for opening the chart and favoriting a strategy remain available
