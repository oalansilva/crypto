## ADDED Requirements

### Requirement: Monitor pair TF, timeframe filter and spark follow the strategy

The Monitor list SHALL display the strategy timeframe next to the pair, offer a timeframe filter of Todos plus the TFs present in the visible crypto list (same rule as Favorites), and draw the minichart with candles of that strategy timeframe. Abrir gráfico and Ver Trades SHALL open on that same timeframe and stay there. The chart SHALL NOT offer a timeframe selector; it SHALL show a read-only label of the strategy timeframe. The list filter SHALL remain and SHALL NOT choose the chart. The board column set stays; the minichart column remains and its visible name is Gráfico.

#### Scenario: Pair TF matches Favorites TF

- **WHEN** a crypto opportunity is rendered on `/monitor`
- **THEN** the TF next to the pair MUST equal that strategy's TF on `/favorites`
- **AND** MUST NOT be a hardcoded 1d

#### Scenario: Filter options come from the visible list

- **WHEN** visible crypto strategies include more than one timeframe
- **THEN** the Monitor list timeframe filter lists Todos and each of those timeframes
- **AND** MUST NOT list only Todos and 1d

#### Scenario: Chart opens on the strategy timeframe with no selector

- **WHEN** the operator clicks Abrir gráfico or Ver Trades on a crypto strategy
- **THEN** the chart `initialTimeframe` is the strategy timeframe
- **AND** the chart shows a read-only label of that timeframe
- **AND** MUST NOT show a timeframe selector
