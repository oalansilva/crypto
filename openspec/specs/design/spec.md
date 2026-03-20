# design Specification

## Purpose
TBD - created by archiving change redesign-backtest-ui. Update Purpose after archive.
## Requirements
### Requirement: Layout Moderno
O formulário SHALL utilizar um sistema de Grid para organizar informações, evitando o "scroll infinito" vertical.
Informações críticas (Símbolo, Timeframe) devem estar no topo ou em destaque.

#### Scenario: Visualização Desktop
- DADO uma tela larga (>1024px)
- ENTÃO o formulário deve exibir configurações e estratégias lado a lado ou em painéis balanceados

### Requirement: Segmented Controls
Para escolhas com menos de 5 opções (ex: Mode, Timeframe populares), a UI SHALL preferir botões segmentados (lista horizontal clicável) ao invés de dropdowns ocultos.

#### Scenario: Selecionar Timeframe
- ENTÃO os timeframes mais comuns (15m, 1h, 4h, 1d) devem estar visíveis como botões clicáveis imediatos.

### Requirement: Feedback Visual
Elementos interativos SHALL fornecer feedback visual imediato em todas as interações do usuário.

#### Scenario: Hover feedback
- **WHEN** the user hovers over an interactive element
- **THEN** the element SHALL display a subtle glow or background color change

#### Scenario: Focus feedback
- **WHEN** an interactive element receives keyboard focus
- **THEN** the element SHALL display a colored border (Azul/Roxo)

#### Scenario: Active/press feedback
- **WHEN** the user presses an interactive element
- **THEN** the element SHALL display a pressed state or solid vibrant color

### Requirement: Estética Glassmorphism
O container e os inputs SHALL respeitar a estética "Glass" com background, border e backdrop filter conforme especificado.

#### Scenario: Glass container styling
- **WHEN** the user views a glass container on a supported browser
- **THEN** the background SHALL use `bg-white/5` or `bg-slate-900/50`
- **AND** the border SHALL use `border-white/10`

#### Scenario: Glass backdrop filter
- **WHEN** the user views a glass container on a supported browser
- **THEN** the element SHALL apply `backdrop-blur-md` where supported

