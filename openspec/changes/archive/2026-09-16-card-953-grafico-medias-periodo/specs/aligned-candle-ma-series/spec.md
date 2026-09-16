## ADDED Requirements

### Requirement: Loaded-history lines stay clipped to the last candle

The inverse of the right-side hole remains closed: filling strategy lines across the loaded candle history SHALL keep every series clipped to the last loaded candle. Extending coverage into older loaded bars MUST NOT paint a point after that candle.

#### Scenario: Filling older bars does not reopen the right-side hole

- **WHEN** strategy lines are calculated across the loaded candle history on `/combo/results` or the Monitor chart
- **THEN** the last visible line point coincides with the last loaded candle
- **AND** the chart MUST NOT show a line ahead of that candle
