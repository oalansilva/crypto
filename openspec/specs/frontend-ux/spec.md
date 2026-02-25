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

