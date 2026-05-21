## ADDED Requirements

### Requirement: Shared chart trade markers are same-candle aware
Strategy chart surfaces SHALL consume trade markers built by a same-candle-aware conversion path when rendering Favorites result charts and Monitor favorite-backed charts.

#### Scenario: Favorites chart renders same-candle trade
- **WHEN** a Favorites analysis chart renders a trade whose entry and exit resolve to the same displayed candle
- **THEN** the chart SHALL show one combined marker for the trade
- **AND** it SHALL NOT show separate `COMPRA` and `VENDA` markers on the same candle for that same trade

#### Scenario: Monitor chart renders same favorite trade
- **WHEN** the Monitor chart modal renders the same favorite trade payload
- **THEN** it SHALL use the same marker conversion behavior as Favorites
- **AND** the marker count and labels SHALL match the favorite analysis chart for that trade set

