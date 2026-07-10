## ADDED Requirements

### Requirement: Canonical strategy transparency manifest
The system SHALL derive one public strategy transparency manifest from the configuration and logic actually used by execution.

#### Scenario: Active strategy resolves a specific manifest
- **WHEN** an active visible strategy is serialized
- **THEN** its manifest SHALL contain a unique PT-BR display name and description
- **AND** SHALL contain the indicators used, effective public parameters, function, panel, scale and participation in entry, exit or risk
- **AND** SHALL NOT contain IDs, dates, `WINNER`, `chain`, versions or generic fallback identity.

#### Scenario: Configuration cannot be proven
- **WHEN** the system cannot resolve the executed configuration for a strategy
- **THEN** it SHALL return an explicit unavailable state
- **AND** SHALL NOT invent a manifest, indicator or generic public identity.

### Requirement: Public identity matches executed behavior
The public name, description and manifest MUST describe only indicators and logic present in the executed strategy.

#### Scenario: EMA RSI legacy key is resolved
- **WHEN** `ema_rsi_fibonacci` is visible and its execution contains EMA and RSI but no Fibonacci calculation
- **THEN** its public identity SHALL describe EMA + RSI
- **AND** SHALL NOT mention Fibonacci.

### Requirement: Safe functional transparency
The common-user manifest SHALL expose the functional behavior required to understand the strategy while excluding technical secrets unrelated to that understanding.

#### Scenario: Common trader receives manifest
- **WHEN** a common trader requests a visible strategy
- **THEN** the response SHALL include configured indicator periods/thresholds, their functions and participation in entry, exit and risk
- **AND** SHALL exclude source code, credentials, tokens, raw diagnostic columns and strategy mutation controls.

### Requirement: Timestamped indicator series
The system SHALL expose only indicator series actually produced by the strategy as timestamped points.

#### Scenario: Series is available
- **WHEN** execution produces an indicator series
- **THEN** every public point SHALL include `timestamp_utc` and a finite value
- **AND** series SHALL be joined to candles by timestamp rather than array position.

#### Scenario: Legacy series lacks trustworthy timestamps
- **WHEN** an indicator array cannot be tied to source timestamps
- **THEN** the API SHALL mark that indicator series unavailable
- **AND** SHALL NOT align it to candle positions by index.

### Requirement: Indicator aliases and diagnostics are filtered
The public manifest and series SHALL contain one canonical entry for each used indicator and SHALL exclude diagnostic-only columns.

#### Scenario: Execution returns aliases and helper columns
- **WHEN** multiple output columns represent one configured indicator or internal calculation helpers
- **THEN** the public response SHALL select the declared canonical series
- **AND** SHALL omit duplicate aliases and diagnostic helpers.

### Requirement: Non-plottable strategy logic remains understandable
The manifest SHALL describe non-plottable conditions in trader language.

#### Scenario: Strategy uses candle pattern or previous-high breakout
- **WHEN** a rule cannot be represented as a continuous indicator series
- **THEN** the manifest SHALL include it in an explanatory logic block
- **AND** SHALL identify whether it participates in entry, exit or risk.

### Requirement: Strategy transparency drift is tested
The repository SHALL maintain an auditable matrix and automated coverage for every active template/strategy.

#### Scenario: Active template catalog changes
- **WHEN** a template is added or its configuration changes
- **THEN** tests SHALL fail if identity is generic, metadata announces an unused indicator, configured indicators are missing, or panel/participation metadata is absent.
