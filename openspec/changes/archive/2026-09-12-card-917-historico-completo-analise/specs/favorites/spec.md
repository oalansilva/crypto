## MODIFIED Requirements

### Requirement: Favorites analysis synchronizes entry and exit signals with Monitor

The Favorites analysis flow MAY refresh current Monitor opportunity data before rendering the analysis. When a matching Monitor opportunity includes signal history, the result MAY include non-duplicate Monitor-derived entry and exit points. That sync SHALL NOT replace a longer saved or regenerated favorite history in the list or on the chart markers. Chart arrows SHALL follow the analysis trade list.

#### Scenario: Saved trades diverge from Monitor signal history

- **WHEN** a favorite has saved trades with old entry/exit timestamps
- **AND** the matching Monitor opportunity has current `signal_history`
- **AND** the user opens full analysis from Favorites
- **THEN** saved or regenerated favorite trades remain visible in the list and as chart markers
- **AND** Monitor `signal_history` MAY add only non-duplicate current operations
- **AND** the chart SHALL NOT show only the recent Monitor recorte while the list shows the full history

#### Scenario: Monitor signal sync unavailable

- **WHEN** Monitor opportunities cannot be loaded or no matching signal history exists
- **AND** the user opens full analysis from Favorites
- **THEN** Favorites falls back to saved/reconstructed trades
- **AND** the failure does not block opening analysis when fallback data exists

#### Scenario: Protected common user opens synced favorite analysis

- **WHEN** a common user opens analysis for a protected favorite
- **AND** Monitor provides redacted signal history
- **THEN** the chart shows entry/exit markers that still match the visible trade list
- **AND** protected parameters, indicators, moving averages, and moving-average values remain hidden
