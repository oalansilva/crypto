## MODIFIED Requirements

### Requirement: Legenda de Indicadores Estilo TradingView
O gráfico SHALL exibir uma legenda textual e acessível para os indicadores ativos declarados no manifesto. A legenda MUST incluir nome, configuração, cor, valor no candle sob o cursor e referências relevantes; na ausência de cursor, MUST usar o último ponto disponível.

#### Scenario: Cursor atualiza legenda por timestamp
- **WHEN** o usuário move o cursor para um candle
- **THEN** a legenda mostra apenas valores com o mesmo timestamp
- **AND** não desloca séries menores para coincidir por posição.

#### Scenario: Legenda permanece compreensível sem cor
- **WHEN** a legenda é lida por tecnologia assistiva ou sem percepção de cor
- **THEN** cada item mantém nome, configuração, valor, painel e rótulo de referência em texto.

### Requirement: Metadados de Indicadores no Backend
O backend SHALL incluir no contrato canônico somente indicadores realmente executados. Cada indicador MUST incluir chave, nome/configuração, cor, função, participação, painel, escala, referências, timeframe, disponibilidade e série de pontos `{timestamp_utc, value}`.

#### Scenario: Resposta da API contém série canônica
- **WHEN** um resultado possui indicadores executados
- **THEN** a API retorna um item por indicador canônico
- **AND** omite aliases duplicados, colunas diagnósticas e séries sem timestamp confiável.

### Requirement: Favorites result chart markers match full trade list
The chart shown after opening full analysis from Favorites SHALL render entry and exit markers for the same complete trade set used by the result trade list while rendering the public strategy indicators for authorized users.

#### Scenario: Favorite analysis has saved history and Monitor sync
- **WHEN** the user opens full analysis from Favorites
- **AND** the result combines saved or regenerated trades with Monitor-synchronized trades
- **THEN** the chart SHALL receive markers for all trades in the combined result trade set
- **AND** the table SHALL not show trades missing from the chart marker source.

#### Scenario: Common user opens protected favorite chart
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the chart SHALL render canonical public indicator overlays and panels when available
- **AND** SHALL keep source code, diagnostics and implementation-only fields hidden
- **AND** trade entry and exit markers SHALL remain visible.

## ADDED Requirements

### Requirement: Shared chart renders manifest-defined panels
The shared Favorites and Monitor chart surface SHALL render only manifest-defined indicator series in the appropriate panel and scale.

#### Scenario: Price and volume indicators render
- **WHEN** the manifest contains EMA, SMA or Bollinger series
- **THEN** they SHALL render over the price panel
- **AND** a configured volume average SHALL render with the volume panel.

#### Scenario: Oscillators render in synchronized panels
- **WHEN** the manifest contains RSI, ADX, ROC, MACD or ATR
- **THEN** each SHALL render in an appropriate synchronized lower panel
- **AND** zero lines, RSI ranges or other declared references SHALL render with text labels.

### Requirement: Chart indicator timeframe is isolated
The chart SHALL never display indicator data from a timeframe different from the visible candles.

#### Scenario: Timeframe changes with recalculated series
- **WHEN** the user changes timeframe and the API returns matching series
- **THEN** the chart SHALL replace all prior indicator series with the matching series.

#### Scenario: Timeframe changes without matching series
- **WHEN** the user changes timeframe and matching series are unavailable
- **THEN** the chart SHALL remove prior indicator series
- **AND** SHALL display an explicit PT-BR unavailable message.

### Requirement: Indicator unavailability is observable
The chart SHALL not silently omit a manifest indicator that lacks usable data.

#### Scenario: Manifest indicator has no usable points
- **WHEN** an indicator is declared but has no finite timestamped points
- **THEN** the UI SHALL identify that indicator as unavailable
- **AND** candles, markers, trades and chart controls SHALL remain usable.

### Requirement: Moving-average colors communicate temporal role
The canonical chart contract SHALL distinguish ordered moving averages by temporal role rather than assigning one color to every EMA or SMA type.

#### Scenario: Three moving averages are rendered
- **WHEN** a strategy executes short, intermediate and long moving averages
- **THEN** the short average SHALL be red, the intermediate average SHALL be orange and the long average SHALL be blue
- **AND** each item SHALL retain its type, period and function in accessible text so meaning does not depend on color alone.

#### Scenario: Moving-average role is not provable
- **WHEN** an indicator does not declare a temporal alias and cannot be ordered safely within a moving-average group
- **THEN** the manifest SHALL keep its standard type color
- **AND** SHALL NOT invent a short/intermediate/long role.
