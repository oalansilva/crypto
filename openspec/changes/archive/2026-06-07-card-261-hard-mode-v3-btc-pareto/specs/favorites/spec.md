## ADDED Requirements

### Requirement: New hard-mode Favorite has visible final metrics
When the HARD MODE V3 run saves a BTC/USDT 1d long Favorite, the system SHALL expose the new Favorite through `/api/favorites/` with the new id, public name, technical strategy name, updated deep backtest metrics, and no pending backtest placeholder.

#### Scenario: Saved Favorite is read back through Favorites API
- **WHEN** the new Favorite is saved and any required refresh completes
- **THEN** `/api/favorites/` returns the Favorite by id with updated metrics and without "Backtest aguardando atualização"

### Requirement: New hard-mode Favorite exposes trade evidence
When the HARD MODE V3 run saves a BTC/USDT 1d long Favorite, the system SHALL expose trade history or equivalent cached trade evidence for the saved Favorite.

#### Scenario: Saved Favorite trades are queryable
- **WHEN** the new Favorite id is requested through `/api/favorites/{id}/trades` or an equivalent endpoint
- **THEN** the response proves the saved Favorite has backtest trade evidence for the final strategy
