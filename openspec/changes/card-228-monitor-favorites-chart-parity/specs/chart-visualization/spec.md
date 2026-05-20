## MODIFIED Requirements

### Requirement: Monitor favorite charts match Favorite analysis charts
When Monitor opens a chart for an opportunity backed by a saved favorite, the chart SHALL use the same favorite analysis trades and candles used by the Favorite analysis chart as the canonical source for markers and strategy-timeframe candles.

#### Scenario: Monitor chart opens for saved favorite with analysis trades
- **WHEN** the user opens the Monitor chart for a saved favorite opportunity
- **AND** `/api/favorites/{favorite_id}/trades` returns trades and candles
- **THEN** the Monitor chart SHALL build entry and exit markers from those returned trades
- **AND** the Monitor chart SHALL use those returned candles for the strategy timeframe
- **AND** the visible sell marker set SHALL match the Favorite analysis chart for the same favorite.

#### Scenario: Favorite analysis source is unavailable
- **WHEN** the user opens the Monitor chart for a saved favorite opportunity
- **AND** the favorite analysis trades endpoint fails or returns no usable trades
- **THEN** the Monitor chart MAY fall back to Monitor signal history and current status markers
- **AND** the chart SHALL remain usable instead of failing closed.
