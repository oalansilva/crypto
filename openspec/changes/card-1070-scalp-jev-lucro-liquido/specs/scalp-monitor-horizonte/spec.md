## MODIFIED Requirements

### Requirement: Scalp module shows rolling 15 min lookback, hurdle, open position and last trade result

The existing Scalp BTCUSDT module on authenticated `/monitor` SHALL show the lookback as «últimos N min» for the consumed prazo (15 minutes while that is the geometry in use), the hurdle in bp, the maker fee in use with "desconto aplicado" only when that discount entered the rate, the applied target and stop, an open position (entry, age, target, stop) when a fill exists, and the last closed-trade **net** P&L in bp and in US$. Negative last-trade results SHALL be as visible as positive ones. When an exit has not filled by prazo+30 s after fill the module SHALL show «posição presa». The module SHALL NOT present a 1 / 2 / 5 minute radio or selector. The module SHALL NOT show «Jev no máximo 1 vez / 15 min» and SHALL NOT show a sleep clock. The module SHALL NOT add copy of the 1.5 s send-wait cap or of «800 ms»; these are send behaviour, not screen content. The consult interval SHALL follow `JEV_TARGET_MS` (30 s by default), as specified by `scalp-jev-consult-cadence`. The module SHALL NOT add imbalance or microprice gauges. The module SHALL NOT show a #1007 cycle ruler or per-horizon hit rate. Copy SHALL NOT say «estratégia lucrativa». The #1001 switch, T, clip, kill banner and Spot-key lock SHALL remain. Landing and Ajuda copy SHALL NOT change in this card.

#### Scenario: Default shows last-fifteen-minutes lookback while off and no version prazo

- **WHEN** an authenticated user opens `/monitor` and no consumed version records a prazo
- **THEN** the scalp module SHALL present «últimos 15 min» as the lookback fact
- **AND** the switch SHALL remain desligado until the user turns it on
- **AND** SHALL NOT show radio options 1 min, 2 min or 5 min

#### Scenario: Hurdle, fee, target and stop are visible

- **WHEN** the module is showing
- **THEN** it SHALL display the hurdle in bp
- **AND** SHALL display the fee in use, with "desconto aplicado" only when the discount entered that fee
- **AND** SHALL display the applied target and stop from the consumed version, or +35 / −28 while that is the geometry in use

#### Scenario: Open position fields after fill

- **WHEN** this scalp has an open position
- **THEN** the module SHALL show entry, age, target and stop
- **AND** age SHALL count from fill (hold of the applied prazo after fill)

#### Scenario: Last trade loss is as visible as gain

- **WHEN** the last closed trade of this scalp is a loss
- **THEN** the module SHALL show that result as net P&L in bp and in US$
- **AND** the loss figure SHALL use the same emphasis vocabulary as a gain (negative vs positive)

#### Scenario: Stuck warning

- **WHEN** the exit has not filled by prazo+30 s after fill
- **THEN** the module SHALL show «posição presa»
- **AND** Operar SHALL remain available on the board

#### Scenario: Cadence copy is fresh touch, not a sleep

- **WHEN** the scalp is ligado and there is no open position
- **THEN** the module SHALL state that Jev asks on the fresh touch
- **AND** SHALL NOT contain «Jev no máximo 1 vez / 15 min»
- **AND** SHALL NOT contain «1,5 s» or «800 ms» as send-cap copy
- **AND** SHALL keep showing the applied lookback fact

#### Scenario: No extra microstructure meters and no ruler

- **WHEN** the module is showing
- **THEN** it SHALL NOT display extra imbalance or microprice meters
- **AND** SHALL NOT display a #1007 cycle ruler
- **AND** SHALL NOT contain «estratégia lucrativa»
