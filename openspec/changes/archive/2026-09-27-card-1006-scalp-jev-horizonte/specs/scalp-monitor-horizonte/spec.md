## ADDED Requirements

### Requirement: Scalp module shows rolling 15 min lookback, hurdle, open position and last trade result

The existing Scalp BTCUSDT module on authenticated `/monitor` SHALL show the lookback as the fact «últimos 15 min» (same vocabulary as T and clip), the hurdle in bp, the maker fee in use, default target 35 bp, default stop −28 bp, an open position (entry, age, target, stop) when a fill exists, and the last closed-trade result in bp and in US$. Negative last-trade results SHALL be as visible as positive ones. When an exit has not filled by 15:30 after fill the module SHALL show «posição presa». The module SHALL NOT present a 1 / 2 / 5 minute radio or selector. The module SHALL NOT show «Jev no máximo 1 vez / 15 min» and SHALL NOT show a sleep clock. The module SHALL NOT add copy of the 1.5 s send-wait cap or of «800 ms» (the panel already shows the ~1 s ask clock; the 1.5 s cap is send behaviour, not a new screen). The module SHALL NOT add imbalance or microprice gauges. The module SHALL NOT show a #1007 cycle ruler or per-horizon hit rate. Copy SHALL NOT say «estratégia lucrativa». The #1001 switch, T, clip, kill banner and Spot-key lock SHALL remain. Landing and Ajuda copy SHALL NOT change in this card.

#### Scenario: Default shows last-fifteen-minutes lookback while off

- **WHEN** an authenticated user opens `/monitor`
- **THEN** the scalp module SHALL present «últimos 15 min» as the lookback fact
- **AND** the switch SHALL remain desligado until the user turns it on
- **AND** SHALL NOT show radio options 1 min, 2 min or 5 min

#### Scenario: Hurdle, fee, target and stop are visible

- **WHEN** the module is showing
- **THEN** it SHALL display the hurdle in bp
- **AND** SHALL display the fee in use (10 bp or 7,5 bp with BNB)
- **AND** SHALL display default target 35 bp and default stop −28 bp

#### Scenario: Open position fields after fill

- **WHEN** this scalp has an open position
- **THEN** the module SHALL show entry, age, target and stop
- **AND** age SHALL count from fill (hold of 15 min after fill)

#### Scenario: Last trade loss is as visible as gain

- **WHEN** the last closed trade of this scalp is a loss
- **THEN** the module SHALL show that result in bp and in US$
- **AND** the loss figure SHALL use the same emphasis vocabulary as a gain (negative vs positive)

#### Scenario: Stuck warning

- **WHEN** the exit has not filled by 15:30 after fill
- **THEN** the module SHALL show «posição presa»
- **AND** Operar SHALL remain available on the board

#### Scenario: Cadence copy is fresh touch, not a 15-minute sleep

- **WHEN** the scalp is ligado and there is no open position
- **THEN** the module SHALL state that Jev asks on the fresh touch
- **AND** SHALL NOT contain «Jev no máximo 1 vez / 15 min»
- **AND** SHALL NOT contain «1,5 s» or «800 ms» as send-cap copy
- **AND** SHALL keep showing lookback «últimos 15 min»

#### Scenario: No extra microstructure meters and no ruler

- **WHEN** the module is showing
- **THEN** it SHALL NOT display extra imbalance or microprice meters
- **AND** SHALL NOT display a #1007 cycle ruler
- **AND** SHALL NOT contain «estratégia lucrativa»
