# Especificação: Design Visual

## ADDED Requirements

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
Elementos interativos SHALL fornecer feedback imediato.
- Hover: Ligeiro brilho ou mudança de fundo.
- Focus: Borda colorida (Azul/Roxo).
- Active: Estado "pressionado" ou cor sólida vibrante.

### Requirement: Estética Glassmorphism
O container e os inputs DEVEM respeitar a estética "Glass":
- Background: `bg-white/5` ou `bg-slate-900/50`
- Border: `border-white/10`
- Backdrop Filter: `backdrop-blur-md` (onde suportado)
