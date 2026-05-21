## ADDED Requirements

### Requirement: Chart marker signal can drive Monitor state parity
Strategy chart surfaces used by Monitor SHALL expose or return enough resolved marker direction information for Monitor to keep summary/current-state labels aligned with the chart.

#### Scenario: Latest marker direction is available
- **WHEN** the Monitor chart marker source resolves a latest valid `Compra` or `Venda` marker
- **THEN** the Monitor state resolver SHALL be able to consume that direction without rebuilding conflicting logic

#### Scenario: Same-candle rules affect latest marker
- **WHEN** same-candle marker normalization changes the latest visible marker from separate actions to a single resolved direction
- **THEN** Monitor state parity SHALL use that resolved direction
- **AND** it SHALL NOT use a stale pre-normalization action from the original raw trade list
