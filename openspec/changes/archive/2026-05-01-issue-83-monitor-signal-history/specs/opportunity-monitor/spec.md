## ADDED Requirements

### Requirement: Monitor chart modal exposes signal history
The opportunity monitor SHALL show recent entry and exit history in the chart modal when the strategy payload includes `signal_history`.

#### Scenario: Strategy payload includes recent signal history
- **WHEN** the trader opens a strategy chart from a visible Monitor row and the payload includes `signal_history`
- **THEN** the chart modal shows `Signal History` with recent `ENTRY` and `EXIT` entries.

#### Scenario: Signal history markers match chart timeframe
- **WHEN** signal history timestamps align with the displayed chart timeframe
- **THEN** the chart modal states that markers are aligned with the chart timeframe.
