## ADDED Requirements

### Requirement: Three gap templates appear in Discovery catalog

The Discovery template catalog SHALL include three templates created through the existing template editor (not `lab_` files, not a one-off script, not a new engine): Canal Donchian + volume; Squeeze de Bollinger; Pullback média longa + RSI + ADX. Templates SHALL NOT pin a timeframe.

#### Scenario: Operator can pick the three gap templates

- **WHEN** the operator opens the Templates axis on Montar
- **THEN** Canal Donchian + volume, Squeeze de Bollinger and Pullback média longa + RSI + ADX are reachable for selection
- **AND** none of them is named with a `lab_` prefix

#### Scenario: Gap templates backtest on 4h 1h 15m

- **WHEN** each of the three templates is run on BTC/USDT at 4h, 1h and 15m
- **THEN** the backtest completes without error on each of those three timeframes

#### Scenario: An existing Discovery template also runs on 1h and 15m

- **WHEN** a template already offered by Discovery (for example Bollinger_Breakout) is run on BTC/USDT at 1h and at 15m
- **THEN** each backtest completes without error
