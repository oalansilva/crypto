## ADDED Requirements

### Requirement: Monitor current state matches latest visible chart signal
Monitor SHALL render the public current-state label from the same latest valid operational signal that the chart displays for the selected strategy, symbol and timeframe.

#### Scenario: Chart resolves latest signal as Venda
- **WHEN** a Monitor opportunity for ADA/USDT, moving-average trend strategy and timeframe `1D` opens with chart data whose latest visible valid signal resolves to `Venda`
- **THEN** the Monitor summary/current-state label SHALL render `Venda`
- **AND** it SHALL NOT render `Compra` for that same opportunity unless the UI exposes a separate explicit explanation for the difference

#### Scenario: Favorite-backed chart data exists
- **WHEN** the Monitor opportunity maps to a saved favorite with trade/marker data
- **THEN** Monitor state display SHALL prefer the resolved latest favorite-backed marker direction for the visible chart context
- **AND** raw opportunity status SHALL remain available only for internal grouping and diagnostics

#### Scenario: No chart signal is available
- **WHEN** Monitor has no favorite-backed marker, signal history or trade evidence for the selected opportunity
- **THEN** Monitor MAY fall back to the backend opportunity state
- **AND** the fallback SHALL stay auditable in tests or diagnostics
