## ADDED Requirements

### Requirement: Monitor chart modal exposes resolved signal context
The opportunity monitor SHALL show explicit resolved signal context when a trader opens a strategy chart from the visible Monitor row.

#### Scenario: Mismatched exit signal opens with resolved state context
- **WHEN** a raw exit signal is downgraded to WAIT because the strategy timeframe or candle context does not match the displayed chart
- **THEN** the chart modal shows the resolved state, strategy timeframe, displayed timeframe, and explanatory context.

#### Scenario: Visible Monitor row opens strategy chart
- **WHEN** the trader activates the chart action on a visible Monitor row
- **THEN** the chart modal opens for that strategy without requiring the hidden expanded detail card.
