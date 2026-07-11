## MODIFIED Requirements

### Requirement: Favorites hide strategy secrets from non-admin users
The Favorites API and UI MUST hide implementation-only strategy secrets from non-admin users while exposing the canonical functional transparency manifest.

#### Scenario: Non-admin lists favorites
- **WHEN** a non-admin user lists saved favorite strategies
- **THEN** each favorite MUST include its specific public name, description and public manifest summary
- **AND** MUST omit source code, credentials, raw diagnostics and unauthorized mutation controls
- **AND** MUST NOT replace the public identity with a generic protected label.

#### Scenario: Admin lists favorites
- **WHEN** an admin user lists saved favorite strategies
- **THEN** each favorite MUST include the same public manifest
- **AND** MAY additionally include original identifiers and technical fields authorized for audit.

### Requirement: Favorites analysis uses Monitor-aligned chart
The Favorites analysis result view SHALL use the shared Monitor-aligned chart and the canonical public indicator contract when candle history is available.

#### Scenario: Favorite analysis opens with candles and indicators
- **WHEN** a user opens full analysis for a favorite with candle and timestamped indicator history
- **THEN** the result SHALL show readable candles, volume, complete trade markers and manifest-defined indicator panels
- **AND** SHALL preserve explicit zoom and the `Analisar` flow.

#### Scenario: Favorite analysis opens without candles
- **WHEN** a user opens favorite analysis and no candles are available
- **THEN** the result SHALL keep an explicit empty chart state
- **AND** the manifesto, summary and trades SHALL remain accessible.

#### Scenario: Common user opens protected favorite analysis
- **WHEN** a common user opens analysis for a protected favorite
- **THEN** the result SHALL show public indicators, parameters and functional explanations from the canonical manifest
- **AND** SHALL keep implementation-only fields and unauthorized regeneration hidden.

### Requirement: Favorites analysis preserves all recoverable trades
The Favorites page SHALL preserve all saved or regenerated trades when opening a full analysis result, even when Monitor synchronization returns a shorter `signal_history`.

#### Scenario: Monitor sync has fewer trades than favorite history
- **WHEN** Monitor synchronization returns fewer trades than the saved or regenerated favorite history
- **THEN** the result trade list and chart markers SHALL retain all recoverable favorite trades.

#### Scenario: Monitor sync adds a missing current trade
- **WHEN** Monitor synchronization returns a non-duplicate trade absent from favorite history
- **THEN** the result SHALL include it once in the list and marker source.

#### Scenario: Common user opens protected favorite
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the result SHALL preserve trades and canonical public indicators
- **AND** SHALL keep source code, diagnostics and unauthorized mutation controls hidden.

## ADDED Requirements

### Requirement: Favorites exposes canonical strategy transparency
Favorites list and analysis responses SHALL expose the same strategy transparency contract used by Monitor.

#### Scenario: Favorite is opened in list and analysis
- **WHEN** a favorite appears in both surfaces
- **THEN** name, description, parameters, indicator metadata and logic explanations SHALL be identical
- **AND** analysis SHALL add timestamped series without redefining the manifest.

#### Scenario: Legacy favorite has aligned cached series but no persisted manifest
- **WHEN** a favorite created before strategy transparency has cached candles and indicator arrays with a proven one-to-one timestamp source
- **AND** its list payload has no usable timestamped transparency series
- **THEN** opening full analysis SHALL request the favorite analysis response that reconstructs the canonical timestamped series
- **AND** `/combo/results` SHALL render the declared overlays or panels
- **AND** the Favorites list SHALL remain a summary payload without duplicating full historical series for every row.

### Requirement: Favorite analysis indicators cover current candles
Opening full favorite analysis SHALL return public indicator series calculated by the backend over the same current OHLCV snapshot returned as chart candles, without rerunning trade optimization.

#### Scenario: Cached analysis is older than canonical candles
- **WHEN** a favorite has saved trades and indicator arrays ending before the current canonical OHLCV history
- **THEN** the analysis response SHALL preserve the saved trades and metrics
- **AND** SHALL recalculate only the declared indicator columns using the favorite's effective parameters
- **AND** every available moving-average series SHALL end at the same timestamp as the last returned candle.

#### Scenario: Current OHLCV reconstruction fails
- **WHEN** current canonical candles cannot be loaded or calculated safely
- **THEN** the analysis SHALL fall back to the proven cached candles and series
- **AND** SHALL NOT align arrays positionally or regenerate trades implicitly.

#### Scenario: Common trader receives current reconstruction
- **WHEN** a non-admin trader is authorized to view the favorite analysis
- **THEN** the response SHALL include current timestamped public series and candles
- **AND** SHALL keep raw `indicator_data`, diagnostics and implementation configuration hidden.
