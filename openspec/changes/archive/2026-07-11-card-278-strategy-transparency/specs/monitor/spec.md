## MODIFIED Requirements

### Requirement: Monitor hides strategy secrets from non-admin users
The Monitor API and UI MUST hide implementation-only strategy secrets from non-admin users while preserving trading decisions and exposing canonical functional transparency.

#### Scenario: Non-admin views monitor opportunity
- **WHEN** a non-admin user opens Monitor
- **THEN** each opportunity MUST show its specific public identity, relevant effective parameters, used indicators and functional explanation
- **AND** MUST omit source code, credentials, raw diagnostics and internal mutation controls.

#### Scenario: Admin views monitor opportunity
- **WHEN** an admin user opens Monitor
- **THEN** each opportunity MUST show the same public manifest
- **AND** MAY additionally show authorized original identifiers and analyzer context.

#### Scenario: Non-admin exports opportunity summary
- **WHEN** a non-admin user exports or copies an opportunity summary
- **THEN** the export MUST include the canonical public identity and functional manifest summary
- **AND** MUST exclude source code, credentials, raw diagnostics and internal-only fields.

### Requirement: Monitor Strategy Description
Monitor SHALL display the canonical public name, description and functional explanation wherever the user needs to understand a strategy.

#### Scenario: Opportunity row and detail show identity
- **WHEN** Monitor renders an opportunity with strategy metadata
- **THEN** row and detail SHALL use the same name and description as Favorites
- **AND** detail SHALL show indicator functions and participation without implementation-only secrets.

### Requirement: Monitor chart modal uses strategy-detail layout
The Monitor chart modal SHALL present a readable strategy-detail surface while preserving existing signal resolution and rendering canonical public indicators.

#### Scenario: User opens Monitor chart
- **WHEN** the user opens an opportunity chart
- **THEN** the main chart SHALL remain dominant with symbol, public identity, signal, timeframe and candle context
- **AND** SHALL render manifest-defined indicator panels, legend and logic blocks when available.

#### Scenario: Common user opens protected strategy chart
- **WHEN** a common user opens a protected strategy chart
- **THEN** the modal SHALL show public effective parameters and functional indicator metadata
- **AND** SHALL NOT expose source code, raw diagnostics or internal implementation payloads.

#### Scenario: Modal is used on mobile
- **WHEN** the viewport is mobile-sized
- **THEN** chart, legend and context panels SHALL remain keyboard/touch usable without horizontal page scrolling.

## ADDED Requirements

### Requirement: Monitor uses favorite transparency series when available
Monitor SHALL use the saved favorite transparency payload as the canonical series source when an opportunity maps to a favorite.

#### Scenario: Saved favorite analysis is available
- **WHEN** Monitor opens a chart for an opportunity with usable favorite analysis
- **THEN** it SHALL use the same candle timestamps, indicator series and manifest as Favorites
- **AND** SHALL preserve Compra/Venda markers, entry/stop lines, zoom, `Abrir Gráfico` and `Ver Trades`.

#### Scenario: Matching timeframe series is unavailable
- **WHEN** Monitor cannot load public series matching the visible timeframe
- **THEN** it SHALL clear indicator panels and show an explicit unavailable state
- **AND** SHALL keep chart and signal actions usable.
