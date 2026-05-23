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

#### Scenario: Monitor list resolves favorite-backed Venda before opening chart
- **WHEN** the Monitor list receives an opportunity whose raw state indicates active position
- **AND** the matching favorite-backed trade markers resolve the latest visible signal as `Venda`
- **THEN** the Monitor list section and opportunity card SHALL render the opportunity as `Venda`
- **AND** it SHALL NOT keep the opportunity under `Em posição · Compra` for the same strategy/timeframe

#### Scenario: No chart signal is available
- **WHEN** Monitor has no favorite-backed marker, signal history or trade evidence for the selected opportunity
- **THEN** Monitor MAY fall back to the backend opportunity state
- **AND** the fallback SHALL stay auditable in tests or diagnostics

#### Scenario: Backend opportunity has favorite cached exit trade
- **WHEN** the backend builds a Monitor opportunity from a saved favorite
- **AND** the raw strategy state indicates an active position
- **AND** the favorite's cached trade history has a latest closed trade event for the same strategy context
- **THEN** the public opportunity payload SHALL resolve to `status=EXIT`
- **AND** `is_holding` SHALL be `false`
- **AND** the next public action SHALL be `entry`
- **AND** the Monitor SHALL render the opportunity as `Venda` without waiting for a separate frontend trade fetch

#### Scenario: Restart after Monitor source change
- **WHEN** the canonical runtime is restarted after a Monitor frontend or backend fix
- **THEN** the frontend build used by `vite preview` SHALL be regenerated from the current source
- **AND** a live preview already answering on port `5173` SHALL NOT cause the restart flow to keep serving a stale `frontend/dist`
