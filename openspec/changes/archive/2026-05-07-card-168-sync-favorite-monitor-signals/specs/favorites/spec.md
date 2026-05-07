## MODIFIED Requirements

### Requirement: Favorites analysis synchronizes entry and exit signals with Monitor
The Favorites analysis flow SHALL refresh current Monitor opportunity data before rendering entry/exit markers and visible trades. When a matching Monitor opportunity includes signal history, the result chart and trade list SHALL use that signal history as the primary source for entry and exit points.

#### Scenario: Saved trades diverge from Monitor signal history
- **WHEN** a favorite has saved trades with old entry/exit timestamps
- **AND** the matching Monitor opportunity has current `signal_history`
- **AND** the user opens full analysis from Favorites
- **THEN** the visible result chart uses markers derived from Monitor `signal_history`
- **AND** the visible trade list uses entries/exits derived from Monitor `signal_history`
- **AND** the old saved trade timestamps are not shown as current result trades

#### Scenario: Monitor signal sync unavailable
- **WHEN** Monitor opportunities cannot be loaded or no matching signal history exists
- **AND** the user opens full analysis from Favorites
- **THEN** Favorites falls back to saved/reconstructed trades
- **AND** the failure does not block opening analysis when fallback data exists

#### Scenario: Protected common user opens synced favorite analysis
- **WHEN** a common user opens analysis for a protected favorite
- **AND** Monitor provides redacted signal history
- **THEN** the chart can show safe entry/exit markers from that history
- **AND** protected parameters, indicators, moving averages, and moving-average values remain hidden
