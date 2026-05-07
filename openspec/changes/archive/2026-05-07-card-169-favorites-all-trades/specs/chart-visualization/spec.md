## ADDED Requirements

### Requirement: Favorites result chart markers match full trade list
The chart shown after opening full analysis from Favorites SHALL render entry and exit markers for the same complete trade set used by the result trade list.

#### Scenario: Favorite analysis has saved history and Monitor sync
- **WHEN** the user opens full analysis from Favorites
- **AND** the result combines saved or regenerated trades with Monitor-synchronized trades
- **THEN** the chart SHALL receive markers for all trades in the combined result trade set
- **AND** the table SHALL not show trades missing from the chart marker source

#### Scenario: Protected favorite chart remains redacted
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the chart SHALL keep protected technical overlays hidden
- **AND** trade entry and exit markers SHALL still reflect the available protected favorite trades
