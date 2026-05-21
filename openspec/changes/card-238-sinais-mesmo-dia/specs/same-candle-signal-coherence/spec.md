## ADDED Requirements

### Requirement: Same-candle trade signals render as one coherent chart event
The system SHALL represent a trade whose entry and exit resolve to the same displayed candle as one explicit same-candle trade event, not as two independent contradictory recommendations.

#### Scenario: Long trade enters and exits on the same daily candle
- **WHEN** a long trade has `entry_time` and `exit_time` on the same displayed 1D candle
- **THEN** the chart marker source SHALL contain one marker for that trade
- **AND** the marker label SHALL communicate both `Compra` and `Venda`
- **AND** the trade list SHALL continue to show the original entry and exit timestamps

#### Scenario: Trade spans different candles
- **WHEN** a trade has `entry_time` and `exit_time` on different displayed candles
- **THEN** the chart marker source SHALL contain separate entry and exit markers
- **AND** their labels SHALL remain direction-aware in Portuguese

#### Scenario: Exit and next entry share one daily candle
- **WHEN** one trade exits and another trade enters on the same displayed 1D candle
- **THEN** the chart marker source SHALL represent the candle with one combined marker for the opposite actions
- **AND** it SHALL NOT render independent `Compra` and `Venda` markers for that same displayed candle

### Requirement: Same-candle signal evidence remains inspectable
The system SHALL keep enough evidence in UI/test output to verify how same-candle signals were represented.

#### Scenario: Test reads marker labels
- **WHEN** automated UI validation inspects the shared chart surface
- **THEN** it SHALL be able to distinguish a same-candle combined marker from separate `COMPRA` and `VENDA` markers
