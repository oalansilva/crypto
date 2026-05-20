## ADDED Requirements

### Requirement: Shared strategy chart surface
Strategy chart surfaces used by Favorites results and Monitor SHALL use a shared chart rendering foundation.

#### Scenario: Favorites renders through shared surface
- **WHEN** a user opens a favorite result with candle history
- **THEN** the result chart SHALL render with the shared dark operational surface
- **AND** it SHALL keep result candles, volume, trade markers and zoom controls from the saved result data.

#### Scenario: Monitor renders through shared surface
- **WHEN** a user opens a Monitor graph modal
- **THEN** the modal SHALL render candles through the same shared chart surface
- **AND** it SHALL keep Monitor-specific timeframe controls, signal context, signal history and entry/stop price lines.

#### Scenario: Existing chart tests remain stable
- **WHEN** Playwright checks existing Favorites and Monitor chart selectors
- **THEN** the shared implementation SHALL preserve the existing `data-testid` contracts for chart shell, chart canvas, zoom controls and visible bar count.
