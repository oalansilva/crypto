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
O gráfico SHALL exibir uma legenda mostrando os indicadores ativos e seus parâmetros.
A legenda MUST incluir o nome do indicador com seus valores de configuração (ex: "SMA(20)", "SMA(50)").
Cada item da legenda MUST usar a mesma cor da linha correspondente no gráfico.

#### Scenario: Exibição de Legenda com Parâmetros Customizados
- DADO que um backtest com SMA Cross (fast=10, slow=30) foi executado
- QUANDO o usuário visualiza o gráfico
- ENTÃO uma legenda é exibida acima do gráfico
- E a legenda mostra "SMA(10)" em vermelho e "SMA(30)" em azul
- E as cores da legenda correspondem às cores das linhas no gráfico

### Requirement: Metadados de Indicadores no Backend
O backend SHALL incluir metadados dos indicadores na resposta da API.
Os metadados MUST incluir: nome do indicador com parâmetros, cor sugerida, e dados da série temporal.

#### Scenario: Resposta da API com Metadados e Parâmetros
- DADO que um backtest foi executado com SMA Cross (fast=15, slow=40)
- QUANDO o frontend solicita os resultados
- ENTÃO a resposta inclui um array de indicadores
- E cada indicador contém `name` (ex: "SMA(15)"), `color`, e `data`

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
The chart shown after opening full analysis from Favorites SHALL render entry and exit markers for the same complete trade set used by the result trade list.

#### Scenario: Favorite analysis has saved history and Monitor sync
- **WHEN** the user opens full analysis from Favorites
- **AND** the result combines saved or regenerated trades with Monitor-synchronized trades
- **THEN** the chart SHALL receive markers for all trades in the combined result trade set
- **AND** the table SHALL not show trades missing from the chart marker source

#### Scenario: Protected favorite chart remains redacted
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the chart SHALL keep protected technical overlays hidden
- **AND** trade entry and exit markers SHALL still reflect the available protected favorite trades

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

