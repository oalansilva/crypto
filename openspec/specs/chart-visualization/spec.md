# chart-visualization Specification

## Purpose
Define chart visualization requirements including SMA/EMA indicators, RSI panel, and Fibonacci levels with consistent styling and legend display.
## Requirements
### Requirement: Configuração de Parâmetros de Estratégia
O formulário Custom Backtest SHALL permitir que o usuário configure os parâmetros da estratégia selecionada.
Para a estratégia SMA Cross, o formulário MUST exibir campos para "Fast SMA" e "Slow SMA".
Os valores padrão MUST ser fast=20 e slow=50.

#### Scenario: Configurar Parâmetros de SMA Cross
- DADO que o usuário está no formulário Custom Backtest
- QUANDO a estratégia "SMA Cross" está selecionada
- ENTÃO campos numéricos para "Fast SMA" e "Slow SMA" são exibidos
- E os valores padrão são 20 e 50 respectivamente
- E o usuário pode alterar esses valores antes de executar o backtest

### Requirement: Cores Personalizadas para Indicadores SMA
O gráfico de candlestick SHALL exibir indicadores de média móvel com cores distintas e consistentes.
A média móvel rápida (fast SMA) MUST ser exibida em vermelho (#ef4444).
A média móvel lenta (slow SMA) MUST ser exibida em azul (#3b82f6).

#### Scenario: Visualização de SMA Cross
- DADO que um backtest com estratégia SMA Cross foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO a linha da média rápida aparece em vermelho
- E a linha da média lenta aparece em azul

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

### Requirement: Visualização de EMA 50 e EMA 200
O gráfico de resultados SHALL exibir as linhas EMA 50 e EMA 200 quando a estratégia EMA RSI Volume é executada. EMA 50 em laranja (#fb923c), EMA 200 em azul (#3b82f6). Legendas "EMA 50" e "EMA 200" com cores correspondentes.

#### Scenario: Visualização de EMA 50 e EMA 200
- **GIVEN** a estratégia EMA RSI Volume foi executada
- **WHEN** o usuário visualiza o gráfico de resultados
- **THEN** a linha EMA 50 é exibida em laranja (#fb923c)
- **AND** a linha EMA 200 é exibida em azul (#3b82f6)
- **AND** a legenda mostra "EMA 50" em laranja e "EMA 200" em azul

### Requirement: Visualização de RSI em Painel Separado
O gráfico SHALL exibir RSI em painel inferior (lower). RSI em roxo (#8b5cf6), legenda "RSI(14)" ou período configurado. Painel RSI MUST incluir linhas de referência em rsi_min e rsi_max.

#### Scenario: Visualização de RSI em Painel Separado
- **GIVEN** um backtest com RSI foi executado
- **WHEN** o usuário visualiza o gráfico
- **THEN** o RSI é exibido em um painel inferior separado
- **AND** a linha RSI é exibida em roxo (#8b5cf6)
- **AND** a legenda mostra "RSI(14)" ou o período configurado
- **AND** linhas de referência são exibidas em rsi_min e rsi_max### Requirement: Sincronização de Indicadores com Parâmetros
Os indicadores visualizados MUST refletir os parâmetros configurados (ema_fast, ema_slow, rsi_period). Backend MUST retornar metadados com name, color, data, panel ("main" para EMAs, "lower" para RSI).### Requirement: Visualização Fibonacci EMA
O gráfico SHALL exibir EMA 200 e níveis Fibonacci (0.5, 0.618) quando a estratégia Fibonacci EMA é executada. Cores distintas para EMA e níveis.

### Requirement: Supported chart surfaces expose explicit zoom controls
Chart surfaces covered by this change SHALL provide explicit zoom-in and zoom-out controls in addition to gesture-based scaling.

#### Scenario: Explicit controls complement existing scaling
- **WHEN** a supported chart surface already allows mouse wheel or trackpad scaling
- **THEN** the UI also provides explicit zoom-in and zoom-out controls

#### Scenario: Explicit controls do not require new data fetch
- **WHEN** the user zooms the chart with explicit controls
- **THEN** the chart updates its visible range without requiring a new candle request by default

### Requirement: Explicit zoom keeps synchronized panels aligned
When a chart surface uses more than one synchronized panel, the system MUST keep the panels aligned after zoom actions.

#### Scenario: Price and RSI panels stay synchronized
- **WHEN** the user zooms a chart that has a main price panel and an RSI panel
- **THEN** both panels keep the same visible time range after the zoom action

#### Scenario: Crosshair context remains coherent after zoom
- **WHEN** the user moves the cursor after a zoom action
- **THEN** tooltip and crosshair data continue to map to the currently visible candle positions

### Requirement: Result charts follow Monitor chart style
Result chart surfaces used by Favorites analysis SHALL follow the Monitor chart visual and interaction pattern.

#### Scenario: Result chart renders operational surface
- **WHEN** a result chart renders candle history
- **THEN** it SHALL use a dark operational canvas with readable axes, grid, candle colors, and crosshair styling
- **AND** it SHALL include volume and moving average overlays where candle data is available

#### Scenario: Result chart supports explicit zoom
- **WHEN** a result chart renders candle history
- **THEN** it SHALL expose explicit zoom in, zoom out, and reset controls
- **AND** zoom actions SHALL update the visible candle range without fetching new candle data

#### Scenario: Result chart supports wheel zoom
- **WHEN** the user scrolls over the chart area
- **THEN** the chart SHALL zoom the visible candle range
- **AND** the page SHALL NOT scroll instead of zooming the chart

### Requirement: Result charts opened from saved items use the shared current candle source
Result chart surfaces opened from saved favorites SHALL prefer the same current market candle source used by Monitor for UI chart rendering.

#### Scenario: Favorites and Monitor align on latest candle
- **WHEN** Monitor and Favorites display the same symbol and timeframe
- **THEN** both chart surfaces use the current market candle source
- **AND** their newest candle date is aligned when the source has current data

### Requirement: Favorites result chart markers include Monitor-synced signal history
Result charts opened from Favorites SHALL include Monitor-synchronized entry and exit signals when current Monitor history is available, while preserving the complete favorite trade marker set.

#### Scenario: Marker source includes Monitor and favorite history
- **WHEN** Favorites opens a result chart for a favorite also present in Monitor
- **AND** Monitor returns current signal history
- **THEN** the chart marker source includes non-duplicate Monitor signal-history trades
- **AND** saved or regenerated favorite trade markers are not dropped only because Monitor history is shorter

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

### Requirement: Monitor chart preserves interaction controls in strategy layout
The Monitor chart surface SHALL preserve explicit zoom controls, wheel zoom, candle count, signal markers and chart rendering when the layout is restyled as a strategy-detail modal.

#### Scenario: User interacts with redesigned Monitor chart
- **WHEN** the user opens the redesigned Monitor chart modal
- **THEN** the chart SHALL expose zoom in, zoom out and reset controls
- **AND** wheel zoom SHALL keep working inside the chart shell
- **AND** visible candle count SHALL update from the chart logical range.

#### Scenario: Signal history exists
- **WHEN** the opportunity has signal history matching the displayed timeframe
- **THEN** the chart SHALL render aligned buy/sell markers
- **AND** the side context SHALL list recent signals without replacing marker behavior.

### Requirement: Shared strategy chart surface
Strategy chart surfaces used by Favorites results and Monitor SHALL use a shared chart rendering foundation.

#### Scenario: Favorites renders through shared surface
- **WHEN** a user opens a favorite result with candle history
- **THEN** the result chart SHALL render with the shared dark operational surface
- **AND** it SHALL keep result candles, volume, trade markers and zoom controls from the saved result data.

#### Scenario: Monitor renders through shared surface
- **WHEN** a user opens a Monitor graph modal
- **THEN** the modal SHALL render candles through the same shared chart surface
- **AND** it SHALL keep Monitor-specific timeframe controls, signal context, signal history and entry/stop price lines.

#### Scenario: Existing chart tests remain stable
- **WHEN** Playwright checks existing Favorites and Monitor chart selectors
- **THEN** the shared implementation SHALL preserve the existing `data-testid` contracts for chart shell, chart canvas, zoom controls and visible bar count.

### Requirement: Strategy chart default visible range
Strategy chart surfaces SHALL open focused on the latest 180 candles when enough candle history is available.

#### Scenario: Chart has more than 180 candles
- **WHEN** a shared strategy chart renders with more than 180 candles
- **THEN** the initial visible range SHALL focus on the latest 180 candles
- **AND** zoom controls SHALL continue to adjust the visible range without fetching new candle data.

#### Scenario: Chart has 180 candles or fewer
- **WHEN** a shared strategy chart renders with 180 or fewer candles
- **THEN** the chart SHALL show the available history without forcing an empty padded 180-candle range.

### Requirement: Monitor chart detail includes Favorites-style trade details
Monitor chart detail SHALL include the same core analysis information users expect from Favorites when the data is available.

#### Scenario: Favorite trade data is available for a Monitor opportunity
- **WHEN** a user opens the Monitor graph modal for an opportunity that maps to a saved favorite
- **THEN** the modal SHALL render a metrics summary and List of trades section using the favorite trade payload
- **AND** the chart SHALL remain the primary visual section.

#### Scenario: Favorite trade data is unavailable
- **WHEN** the favorite trade payload cannot be loaded
- **THEN** the modal SHALL fall back to closed trades derived from Monitor signal history
- **AND** the modal SHALL remain usable without blocking the chart.

### Requirement: Favorites and Monitor share trade detail presentation
Favorites result graphs and Monitor graph details SHALL render closed-trade metrics and trade rows through the same shared trade detail component.

#### Scenario: User opens the Favorites result graph flow
- **WHEN** the Favorites result page renders strategy trades
- **THEN** it SHALL use the shared trade detail component
- **AND** it SHALL keep the existing export action available.

#### Scenario: User opens the Monitor graph modal
- **WHEN** the Monitor graph modal renders strategy trades
- **THEN** it SHALL use the same shared trade detail component as Favorites.

### Requirement: Monitor favorite charts match Favorite analysis charts
When Monitor opens a chart for an opportunity backed by a saved favorite, the chart SHALL use the same favorite analysis trades and candles used by the Favorite analysis chart as the canonical source for markers and strategy-timeframe candles.

#### Scenario: Monitor chart opens for saved favorite with analysis trades
- **WHEN** the user opens the Monitor chart for a saved favorite opportunity
- **AND** `/api/favorites/{favorite_id}/trades` returns trades and candles
- **THEN** the Monitor chart SHALL build entry and exit markers from those returned trades
- **AND** the Monitor chart SHALL use those returned candles for the strategy timeframe
- **AND** the chart marker text SHALL use Portuguese labels `COMPRA` and `VENDA` instead of `BUY` and `SELL`.
- **AND** the visible sell marker set SHALL match the Favorite analysis chart for the same favorite.
- **AND** the Monitor chart SHALL NOT add a duplicate current-status marker on top of an equivalent favorite trade marker.

#### Scenario: Favorite analysis source is unavailable
- **WHEN** the user opens the Monitor chart for a saved favorite opportunity
- **AND** the favorite analysis trades endpoint fails or returns no usable trades
- **THEN** the Monitor chart MAY fall back to Monitor signal history and current status markers
- **AND** the chart SHALL remain usable instead of failing closed.

### Requirement: Chart modal renders above app chrome
Chart modal overlays SHALL render outside nested app containers with enough stacking priority to remain visible above navigation and page chrome.

#### Scenario: User opens a chart modal on Monitor
- **WHEN** the chart modal is opened
- **THEN** the overlay appears above the application chrome and remains usable

### Requirement: Chart user-facing labels are localized
Chart visualization UI SHALL use Portuguese labels for trader-facing messages introduced by this change.

#### Scenario: Chart data is unavailable
- **WHEN** a chart has no candle data to render
- **THEN** the user-facing empty state is displayed in Portuguese

### Requirement: Trade Marker Phase Is Not Inferred From Text Alone

Chart marker helpers SHALL distinguish trade phase from visual action labels.

#### Scenario: Short sell marker is an entry

- **GIVEN** a trade marker was built for a short entry
- **AND** its visible label is `VENDA`
- **WHEN** consumers ask for marker signal phase
- **THEN** the marker SHALL be classified as entry, not exit

#### Scenario: Short buy marker is an exit

- **GIVEN** a trade marker was built for a short exit or cover
- **AND** its visible label is `COMPRA`
- **WHEN** consumers ask for marker signal phase
- **THEN** the marker SHALL be classified as exit, not entry

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

