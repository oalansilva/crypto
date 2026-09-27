## ADDED Requirements

### Requirement: Monitor list, filter, spark and chart use the strategy timeframe

`/monitor` SHALL show, filter and open the chart on the strategy timeframe — the same value as the TF column of that row in `/favorites`. The list MUST NOT treat a 4h crypto favorite as 1d. The chart opened from Abrir gráfico / Ver Trades SHALL display that strategy timeframe as a read-only label and MUST NOT offer a timeframe selector. Signal, position and stop stay those of the strategy on that timeframe. Stock action charts remain 1d only. Layout of Status, Preço, Distância, Tags, Operar and Par / Estratégia SHALL NOT be redesigned. The minichart column SHALL remain; its visible header SHALL be Gráfico (the 7d label no longer applies). The list timeframe filter (Todos plus TFs present in the list) SHALL remain and SHALL NOT choose the chart.

#### Scenario: BTC 4h shows 4h next to the pair

- **WHEN** a crypto favorite BTC/USDT on 4h is visible in `/favorites`
- **AND** the operator opens `/monitor`
- **THEN** that strategy's row shows 4h next to the pair
- **AND** MUST NOT show «Gráfico 1d» or «tf 1d»

#### Scenario: Timeframe filter lists Todos plus TFs present in the list

- **WHEN** the Monitor list has at least one 4h strategy and one 1d strategy
- **THEN** the timeframe filter options are Todos, 4h and 1d
- **AND** MUST NOT be only Todos and 1d

#### Scenario: Filter 4h hides 1d rows

- **WHEN** the same list has at least one 4h and one 1d
- **AND** the operator chooses the 4h filter
- **THEN** only 4h strategies remain visible

#### Scenario: Filter 1d hides 4h rows

- **WHEN** the same list has at least one 4h and one 1d
- **AND** the operator chooses the 1d filter
- **THEN** only 1d strategies remain visible

#### Scenario: Filter Todos shows every strategy timeframe

- **WHEN** the operator chooses Todos on the timeframe filter
- **THEN** 4h and 1d strategies remain visible together

#### Scenario: Minichart uses strategy timeframe candles

- **WHEN** the operator views the 4h row minichart
- **THEN** the candles are 4h
- **AND** MUST NOT be 1d candles labelled as 7d

#### Scenario: Abrir gráfico and Ver Trades start on the strategy timeframe

- **WHEN** the operator clicks Abrir gráfico or Ver Trades on that 4h strategy
- **THEN** the chart starts on 4h (candles and read-only label)
- **AND** MUST NOT start on 1d
- **AND** the chart stays on 4h
- **AND** the list still shows 4h next to the pair

#### Scenario: Chart has no timeframe selector

- **WHEN** the chart is open from Abrir gráfico or Ver Trades on that 4h strategy
- **THEN** the chart shows a read-only strategy timeframe label (4h)
- **AND** MUST NOT show a timeframe selector
- **AND** MUST NOT show clickable 15m, 1h, 1d or «Estratégia (4H)» buttons
- **AND** MUST NOT show `role="group"` «Selecionar timeframe do gráfico»
- **AND** the candles stay on the strategy timeframe

#### Scenario: Stock action stays 1d

- **WHEN** the operator opens the chart of a stock action
- **THEN** the chart timeframe remains 1d only
