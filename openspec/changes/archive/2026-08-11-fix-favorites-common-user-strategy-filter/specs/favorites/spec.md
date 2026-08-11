## MODIFIED Requirements

### Requirement: Favorites Strategy filter uses only strategy labels
The Favorites page Strategy filter MUST list and match only strategy labels, not symbols, timeframes, hours, or free-form favorite names. For protected favorites shown to common users, the system MUST provide a distinct safe strategy display label for filtering while keeping raw strategy implementation details redacted.

#### Scenario: Favorites page builds Strategy options
- **WHEN** the Favorites page loads crypto favorites
- **THEN** the Strategy filter options MUST be derived from the favorite strategy label
- **AND** Strategy options MUST NOT include symbol text such as `BTC/USDT` or `ETH/USDT`
- **AND** Strategy options MUST NOT include timeframe text such as `1h` or `4h`
- **AND** timeframe values MUST remain available only in the Time filter

#### Scenario: User filters by strategy label
- **WHEN** the user selects a Strategy option
- **THEN** the page MUST show favorites whose strategy label matches that option
- **AND** the filter MUST not depend on the favorite nickname

#### Scenario: Common user filters protected favorites by safe strategy label
- **WHEN** a common user opens Favorites with multiple protected strategies
- **THEN** the Strategy filter MUST include distinct safe strategy labels instead of only the generic protected label
- **AND** selecting a safe strategy label MUST filter the list to favorites with that label
- **AND** the page MUST keep raw strategy names, parameters, and indicators hidden

#### Scenario: Common user opens protected favorite chart
- **WHEN** a common user opens the chart or full analysis for a protected favorite
- **THEN** the chart title MUST show the same safe strategy label used by the Favorites filter
- **AND** the chart MUST NOT show raw strategy names, parameters, or protected indicator values

#### Scenario: Favorite chart opens when monitor sync is slow
- **WHEN** a user opens full analysis for a favorite that already has saved chart context
- **AND** monitor opportunity refresh or trade sync is slow
- **THEN** the system MUST open the favorite chart using saved or current candle data without waiting indefinitely for monitor sync
- **AND** monitor sync MAY be skipped for that open
