## ADDED Requirements

### Requirement: Monitor chart modal uses strategy-detail layout
The Monitor chart modal SHALL present the selected opportunity as a readable strategy-detail surface inspired by the card #218 `Estrategia.html` reference, while preserving existing signal resolution and data behavior.

#### Scenario: User opens Monitor chart
- **WHEN** the user opens a Monitor opportunity chart
- **THEN** the modal SHALL show a compact strategy header with symbol, public strategy label, resolved signal and timeframe/candle context
- **AND** the main chart SHALL remain the dominant visible surface
- **AND** supporting context SHALL be organized in compact panels instead of a long technical stack.

#### Scenario: Common user opens protected strategy chart
- **WHEN** the chart belongs to a protected strategy and the viewer is not allowed to see parameters
- **THEN** the modal SHALL keep parameter values redacted
- **AND** the new layout SHALL NOT expose original protected implementation details.

#### Scenario: Modal is used on mobile
- **WHEN** the viewport is mobile-sized
- **THEN** the modal SHALL keep the chart and context panels usable without horizontal scrolling.
