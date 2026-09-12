## MODIFIED Requirements

### Requirement: Favorites result chart markers include Monitor-synced signal history

Result charts opened from Favorites SHALL include Monitor-synchronized entry and exit signals when current Monitor history is available, while preserving the complete favorite trade marker set. Monitor `signal_history` SHALL NOT become the exclusive marker source when the analysis trade list is longer.

#### Scenario: Marker source includes Monitor and favorite history

- **WHEN** Favorites opens a result chart for a favorite also present in Monitor
- **AND** Monitor returns current signal history
- **THEN** the chart marker source includes non-duplicate Monitor signal-history trades
- **AND** saved or regenerated favorite trade markers are not dropped only because Monitor history is shorter
- **AND** the implementation SHALL NOT replace the analysis trade-list markers with only the recent Monitor recorte

### Requirement: Favorites result chart markers match full trade list

The chart shown after opening full analysis from Favorites or Combo (`/combo/results`) SHALL render entry and exit markers for the same complete trade set used by the result trade list while rendering the public strategy indicators for authorized users. The marker origin SHALL be the analysis list (`buildTradeMarkers` on that list), not a recent Monitor signal recorte.

#### Scenario: Favorite analysis has saved history and Monitor sync

- **WHEN** the user opens full analysis from Favorites
- **AND** the result combines saved or regenerated trades with Monitor-synchronized trades
- **THEN** the chart SHALL receive markers for all trades in the combined result trade set
- **AND** the table SHALL not show trades missing from the chart marker source
- **AND** a short `signal_history` SHALL NOT hide older list operations from the chart series

#### Scenario: Common user opens protected favorite chart

- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the chart SHALL render canonical public indicator overlays and panels when available
- **AND** SHALL keep source code, diagnostics and implementation-only fields hidden
- **AND** trade entry and exit markers SHALL remain visible
- **AND** those markers SHALL still match the visible trade list 1:1
