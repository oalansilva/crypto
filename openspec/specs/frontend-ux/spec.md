# frontend-ux Specification

## Purpose
TBD - created by archiving change pause-resume-simulation. Update Purpose after archive.
## Requirements
### Requirement: Controle via UI
A interface DEVE (MUST) fornecer mecanismos claros para o usuário interromper e controlar a execução.

#### Scenario: Controle de Pausa
> Como um usuário
> Eu quero pausar uma simulação em execução
> Para que eu possa liberar recursos do meu computador

- A barra de progresso DEVE exibir um botão [PAUSAR] quando uma simulação estiver `RUNNING` (Rodando) ou `OPTIMIZING` (Otimizando).
- Clicar em [PAUSAR] DEVE enviar uma requisição para `/api/backtest/pause/{id}` e atualizar o status da UI para `PAUSING...` (Pausando) e então `PAUSED` (Pausado).

### Requirement: Notificação de Retomada
O sistema DEVE (MUST) informar proativamente o usuário sobre trabalhos pendentes ou interrompidos.

#### Scenario: Prompt de Retomada
> Como um usuário
> Eu quero saber se tenho simulações não finalizadas
> Para que eu possa escolher retomá-las

- Ao carregar a aplicação, o sistema DEVE verificar se há jobs com status `PAUSED` ou `RUNNING` (interrompidos).
- Se um job pausado for encontrado, um modal DEVE aparecer: "Estratégia Sem Nome (45% concluída) foi pausada. Continuar? [Sim] [Não]".
- Clicar em [Sim] DEVE chamar `/api/backtest/resume/{id}` e restaurar a visualização de progresso.

### Requirement: Combo Configure supports market selection (Crypto vs US Stocks)
The Combo Configure UI MUST allow the user to switch between **Crypto** and **US Stocks (NASDAQ-100)** markets.

#### Scenario: User selects Crypto market
- **WHEN** the user selects market `crypto`
- **THEN** the Symbol control behaves as it does today (crypto pairs), and requests omit `data_source` (defaulting to crypto)

#### Scenario: User selects US Stocks market
- **WHEN** the user selects market `us-stocks`
- **THEN** the Symbol control lists NASDAQ-100 tickers and requests include `data_source=stooq`

### Requirement: US Stocks market enforces EOD timeframe
When market `us-stocks` is selected, the system MUST enforce timeframe `1d` for Stooq EOD backtests.

#### Scenario: User attempts intraday timeframe for US Stocks
- **WHEN** the user selects market `us-stocks` and selects timeframe other than `1d`
- **THEN** the UI prevents the run and indicates that US Stocks via Stooq supports EOD (1D) only

### Requirement: Favorites route supports responsive navigation and layout
The UI MUST provide a responsive layout for the Favorites route (`/favorites`) optimized for mobile use.

#### Scenario: Navigation remains accessible on mobile
- **WHEN** the user opens the Favorites screen on a mobile viewport
- **THEN** navigation to other primary screens remains accessible (e.g., via a compact header, drawer, or bottom navigation)

#### Scenario: Filters and search are usable on mobile
- **WHEN** the user uses filters/search on a mobile viewport
- **THEN** the controls are reachable without precision tapping and do not require horizontal scrolling

### Requirement: Favorites screen avoids horizontal scrolling on mobile
The UI MUST avoid horizontal scrolling for the main Favorites content on mobile.

#### Scenario: Content fits within viewport
- **WHEN** the viewport is below the mobile breakpoint
- **THEN** the Favorites list/cards fit within the viewport width and wrap/truncate long text appropriately

### Requirement: Favorites screen is covered by E2E tests
The system MUST provide E2E tests that validate the Favorites screen core workflow.

#### Scenario: Favorites loads successfully
- **WHEN** the E2E test opens the Favorites route
- **THEN** the Favorites list renders without client-side errors

#### Scenario: View Results triggers backtest and navigates to results
- **WHEN** the E2E test clicks the "View Results" action for a favorite
- **THEN** the UI triggers a backtest request and navigates to the results page

### Requirement: Favorites includes an Asset Type dropdown
The UI MUST include an Asset Type dropdown control on the Favorites screen.

#### Scenario: Dropdown provides expected options
- **WHEN** the user opens the Favorites screen
- **THEN** the Asset Type dropdown contains options: All, Crypto, Stocks

#### Scenario: Changing the dropdown updates the visible list
- **WHEN** the user changes the Asset Type dropdown
- **THEN** the Favorites list updates immediately to reflect the selection

### Requirement: Favorites-only dataset is used
The UI MUST use only the Favorites dataset for the dashboard.

#### Scenario: No non-favorite symbols appear
- **WHEN** the dashboard renders
- **THEN** only favorites appear in the dashboard list

### Requirement: Candlestick chart uses a consistent visual language
The UI MUST render a candlestick chart with clear up/down candle colors and readable axes.

#### Scenario: Candle colors represent direction
- **WHEN** candles are rendered
- **THEN** bullish candles use one color and bearish candles use another color

#### Scenario: Chart remains usable on small screens
- **WHEN** the chart is rendered on a small viewport
- **THEN** labels do not overlap excessively and the user can still interpret the trend

### Requirement: Monitor provides controls for In Portfolio and card mode
The UI MUST provide controls on the Monitor screen to:
- filter the list by In Portfolio vs All
- toggle per-card mode (Price vs Strategy)
- select per-card timeframe in Price mode

#### Scenario: Filter toggle exists
- **WHEN** the user opens Monitor
- **THEN** the UI provides a control to switch between In Portfolio and All

#### Scenario: Per-card toggle exists
- **WHEN** the user views a symbol card
- **THEN** the card provides a toggle control to switch between Price and Strategy modes

#### Scenario: Per-card timeframe selector exists
- **WHEN** the card is in Price mode
- **THEN** the card provides a timeframe selector with allowed options for the asset type

### Requirement: Monitor candles UX remains responsive on mobile
The UI MUST remain responsive on mobile when fetching candles after timeframe changes.

#### Scenario: No full-screen blocking overlay
- **WHEN** the user changes timeframe on a Monitor card
- **THEN** the UI does not show a full-screen blocking overlay; only the chart area indicates loading

#### Scenario: Scroll remains possible
- **WHEN** candle data is loading
- **THEN** the user can still scroll the Monitor list

