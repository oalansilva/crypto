## ADDED Requirements

### Requirement: Monitor chart modal keeps the chart mounted during data updates
The Monitor chart modal SHALL keep the visible chart canvas mounted after opening while markers, price lines, trade context, tooltip data, or refreshed candles are applied.

#### Scenario: Async chart context arrives after modal opens
- **WHEN** a trader opens a Monitor chart
- **AND** asynchronous marker, trade, or candle context updates after the initial render
- **THEN** the chart canvas remains present and visible
- **AND** the modal remains open until the trader explicitly closes it.

#### Scenario: Chart data updates without destroying the chart
- **WHEN** the Monitor chart receives updated candles, markers, or price lines for the same modal session
- **THEN** the existing chart instance updates its series data in place
- **AND** the chart container is not removed as part of that routine update.
