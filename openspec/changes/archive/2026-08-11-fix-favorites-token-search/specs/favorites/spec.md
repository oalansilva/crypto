## ADDED Requirements

### Requirement: Favorites search supports combined terms
Favorites SHALL match free-text searches when all typed terms appear across the combined favorite identity, including symbol, quote, strategy name, displayed strategy label, favorite name, description, and timeframe.

#### Scenario: Search spans symbol and strategy
- **WHEN** a user searches Favorites for `BTC/USDT USDT multi ma crossoverV2`
- **THEN** the BTC/USDT favorite using `multi_ma_crossoverV2` SHALL remain visible when other filters allow it

#### Scenario: Existing single-field search remains supported
- **WHEN** a user searches Favorites for a symbol, strategy word, or favorite name fragment
- **THEN** matching favorites SHALL remain visible
