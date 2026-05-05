## MODIFIED Requirements

### Requirement: Favorites Strategy filter uses only strategy labels
The Favorites page Strategy filter MUST list and match only strategy labels, not symbols, timeframes, hours, or free-form favorite names.

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
