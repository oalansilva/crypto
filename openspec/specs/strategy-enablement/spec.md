# strategy-enablement Specification

## Purpose
TBD - created by archiving change enable-rsi-bb-strategies. Update Purpose after archive.
## Requirements
### Requirement: Habilitar Estratégia RSI Reversal
O formulário Custom Backtest SHALL permitir selecionar a estratégia "RSI Reversal".
A estratégia MUST estar habilitada (não desabilitada) para seleção.

#### Scenario: Selecionar RSI Reversal
- DADO que o usuário está no formulário Custom Backtest
- QUANDO o usuário clica no botão "RSI Reversal"
- ENTÃO a estratégia é selecionada
- E campos de parâmetros específicos para RSI aparecem

### Requirement: Configuração de Parâmetros RSI
O formulário SHALL exibir campos para configurar parâmetros da estratégia RSI Reversal.
Os campos MUST incluir: RSI Period, Oversold Level, Overbought Level.
Os valores padrão MUST ser: period=14, oversold=30, overbought=70.

#### Scenario: Configurar Parâmetros RSI
- DADO que RSI Reversal está selecionada
- QUANDO o usuário visualiza o formulário
- ENTÃO campos "RSI Period", "Oversold", "Overbought" são exibidos
- E os valores padrão são 14, 30, 70 respectivamente

### Requirement: Habilitar Estratégia Bollinger Bands
O formulário Custom Backtest SHALL permitir selecionar a estratégia "Bollinger Bands".
A estratégia MUST estar habilitada (não desabilitada) para seleção.

#### Scenario: Selecionar Bollinger Bands
- DADO que o usuário está no formulário Custom Backtest
- QUANDO o usuário clica no botão "Bollinger Bands"
- ENTÃO a estratégia é selecionada
- E campos de parâmetros específicos para BB aparecem

### Requirement: Configuração de Parâmetros Bollinger Bands
O formulário SHALL exibir campos para configurar parâmetros da estratégia Bollinger Bands.
Os campos MUST incluir: BB Period, Standard Deviation, Exit Mode.
Os valores padrão MUST ser: period=20, std=2.0, exit_mode='mid'.

#### Scenario: Configurar Parâmetros BB
- DADO que Bollinger Bands está selecionada
- QUANDO o usuário visualiza o formulário
- ENTÃO campos "BB Period", "Std Dev", "Exit Mode" são exibidos
- E os valores padrão são 20, 2.0, 'mid' respectivamente

### Requirement: Visualização de Indicador RSI
O gráfico de resultados SHALL exibir a linha do indicador RSI.
A linha RSI MUST ser exibida em roxo (#8b5cf6).
A legenda MUST mostrar "RSI(14)" (ou o valor configurado).

#### Scenario: Visualizar RSI no Gráfico
- DADO que um backtest com RSI Reversal foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO uma linha roxa representando o RSI é exibida
- E a legenda mostra "RSI(14)" em roxo

### Requirement: Visualização de Bandas de Bollinger
O gráfico de resultados SHALL exibir as três bandas de Bollinger (upper, middle, lower).
As bandas MUST usar cores distintas: upper/lower em azul claro (#60a5fa), middle em amarelo (#fbbf24).
A legenda MUST mostrar "BB Upper(20,2)", "BB Middle(20,2)", "BB Lower(20,2)".

#### Scenario: Visualizar Bollinger Bands no Gráfico
- DADO que um backtest com Bollinger Bands foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO três linhas representando as bandas são exibidas
- E a legenda mostra "BB Upper(20,2)", "BB Middle(20,2)", "BB Lower(20,2)" com cores correspondentes

### Requirement: Metadados de Indicadores no Backend
O backend SHALL incluir metadados para indicadores RSI e Bollinger Bands.
Os metadados MUST incluir nome formatado com parâmetros e cores específicas.

#### Scenario: Resposta da API com Indicadores RSI e BB
- DADO que um backtest com RSI ou BB foi executado
- QUANDO o frontend solicita os resultados
- ENTÃO a resposta inclui indicadores com `name` formatado (ex: "RSI(14)"), `color`, e `data`

### Requirement: Habilitar Estratégia ESTRATEGIAAXS
O formulário Custom Backtest SHALL permitir selecionar a estratégia "ESTRATEGIAAXS". O frontend DEVE renderizar os campos de parâmetros dinamicamente com base nos metadados do backend. O backend DEVE expor metadados para os 3 parâmetros (Media Curta EMA=6, Media Longa SMA=38, Media Intermediaria SMA=21). A estratégia DEVE suportar Stop Loss, Take Profit e otimização e estar disponível em `/optimize/parameters` e `/optimize/risk`. O gráfico de resultados SHALL exibir as médias (Curta Vermelho, Longa Azul, Intermediaria Laranja).

### Requirement: Habilitar Estratégia EMA 50/200 + RSI + Volume
O formulário SHALL permitir selecionar a estratégia "EMA 50/200 + RSI + Volume" (ID "emarsivolume"). Parâmetros: ema_fast, ema_slow, rsi_period, rsi_min, rsi_max com defaults 50, 200, 14, 40, 50. A estratégia MUST gerar compra quando preço acima EMA 200, pullback na EMA 50 e RSI entre rsi_min e rsi_max; venda quando preço cruza abaixo EMA 50 ou RSI &lt; rsi_min. MUST suportar otimização e Stop Loss/Take Profit. Backend SHALL incluir metadados completos.### Requirement: Habilitar Estratégia Fibonacci + EMA 200
O formulário SHALL permitir selecionar "Fibonacci (0.5 / 0.618) + EMA 200" (ID "fibonacciema"). Parâmetros: ema_period=200, swing_lookback=20, fib_level_1=0.5, fib_level_2=0.618, level_tolerance=0.005. A estratégia MUST detectar swing high/low, calcular níveis Fibonacci e gerar compra quando preço acima EMA 200 e dentro da tolerância de um nível Fib com bounce. MUST suportar otimização e Stop Loss/Take Profit.

### Requirement: Template Editing via API (REQ-STRAT-EDIT-001)
O sistema SHALL permitir atualizar templates de estratégia via API REST. PUT /api/combos/meta/{template_name} atualiza optimization_schema para templates com is_readonly=0; 403 para templates somente-leitura; 400 para ranges inválidos (min >= max).### Requirement: Template Clonagem (REQ-STRAT-CLONE-001)
O sistema SHALL permitir clonar templates. POST /api/combos/meta/{name}/clone?new_name=... cria novo template com is_readonly=0, is_prebuilt=0; 409 se nome duplicado.

### Requirement: UI de Edição de Template (REQ-STRAT-UI-001)
O sistema SHALL fornecer interface em `/combo/edit/{template_name}` com formulário de min/max/step, botão Salvar (PUT), validação em tempo real. Modo Avançado com editor JSON, syntax highlighting e validação.

### Requirement: Acesso ao Editor pela Página de Seleção (REQ-STRAT-NAV-001)
Em `/combo/select`, templates customizados mostram botão "Editar"; templates pré-construídos mostram "Clonar & Editar" com modal de nome e redirecionamento ao editor do clone.