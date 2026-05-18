## MODIFIED Requirements

### Requirement: Strategy chart default visible range
Strategy chart surfaces SHALL open focused on the latest 180 candles when enough candle history is available.

#### Scenario: Chart has more than 180 candles
- **WHEN** a shared strategy chart renders with more than 180 candles
- **THEN** the initial visible range SHALL focus on the latest 180 candles
- **AND** zoom controls SHALL continue to adjust the visible range without fetching new candle data.

#### Scenario: Chart has 180 candles or fewer
- **WHEN** a shared strategy chart renders with 180 or fewer candles
- **THEN** the chart SHALL show the available history without forcing an empty padded 180-candle range.

### Requirement: Monitor chart detail includes Favorites-style trade details
Monitor chart detail SHALL include the same core analysis information users expect from Favorites when the data is available.

#### Scenario: Favorite trade data is available for a Monitor opportunity
- **WHEN** a user opens the Monitor graph modal for an opportunity that maps to a saved favorite
- **THEN** the modal SHALL render a metrics summary and List of trades section using the favorite trade payload
- **AND** the chart SHALL remain the primary visual section.

#### Scenario: Favorite trade data is unavailable
- **WHEN** the favorite trade payload cannot be loaded
- **THEN** the modal SHALL fall back to closed trades derived from Monitor signal history
- **AND** the modal SHALL remain usable without blocking the chart.

### Requirement: Favorites and Monitor share trade detail presentation
Favorites result graphs and Monitor graph details SHALL render closed-trade metrics and trade rows through the same shared trade detail component.

#### Scenario: User opens the Favorites result graph flow
- **WHEN** the Favorites result page renders strategy trades
- **THEN** it SHALL use the shared trade detail component
- **AND** it SHALL keep the existing export action available.

#### Scenario: User opens the Monitor graph modal
- **WHEN** the Monitor graph modal renders strategy trades
- **THEN** it SHALL use the same shared trade detail component as Favorites.
