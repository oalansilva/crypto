# strategy-enablement Specification Delta

## ADDED Requirements

### Requirement: Habilitar Estratégia EMA 50/200 + RSI + Volume
O formulário Custom Backtest SHALL permitir selecionar a estratégia "EMA 50/200 + RSI + Volume".
A estratégia MUST estar habilitada (não desabilitada) para seleção.
A estratégia MUST ser identificada pelo ID "emarsivolume".

#### Scenario: Selecionar EMA RSI Volume Strategy
- DADO que o usuário está no formulário Custom Backtest
- QUANDO o usuário seleciona a estratégia "EMA 50/200 + RSI + Volume"
- ENTÃO a estratégia é selecionada
- E campos de parâmetros específicos para a estratégia aparecem dinamicamente

### Requirement: Configuração de Parâmetros EMA RSI Volume
O formulário SHALL exibir campos para configurar parâmetros da estratégia EMA RSI Volume.
Os campos MUST incluir: EMA Fast Period, EMA Slow Period, RSI Period, RSI Min, RSI Max.
Os valores padrão MUST ser: ema_fast=50, ema_slow=200, rsi_period=14, rsi_min=40, rsi_max=50.

#### Scenario: Configurar Parâmetros EMA RSI Volume
- DADO que "EMA 50/200 + RSI + Volume" está selecionada
- QUANDO o usuário visualiza o formulário
- ENTÃO campos "EMA Fast", "EMA Slow", "RSI Period", "RSI Min", "RSI Max" são exibidos
- E os valores padrão são 50, 200, 14, 40, 50 respectivamente

### Requirement: Lógica de Compra EMA RSI Volume
A estratégia MUST gerar sinal de compra quando TODAS as condições são atendidas:
- Preço está acima da EMA 200 (filtro de tendência de alta)
- Preço faz pullback até a EMA 50
- RSI está entre rsi_min e rsi_max (zona de pullback, padrão 40-50)

#### Scenario: Sinal de Compra Válido
- DADO que o preço está acima da EMA 200
- E o preço cruza acima da EMA 50 (recuperação do pullback)
- E o RSI está entre 40 e 50
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de compra (1) é gerado

#### Scenario: Sinal de Compra Bloqueado por Tendência de Baixa
- DADO que o preço está abaixo da EMA 200
- E o preço cruza acima da EMA 50
- E o RSI está entre 40 e 50
- QUANDO a estratégia avalia o sinal
- ENTÃO NENHUM sinal de compra é gerado (filtro de tendência bloqueia)

### Requirement: Lógica de Venda EMA RSI Volume
A estratégia MUST gerar sinal de venda quando QUALQUER condição é atendida:
- Preço cruza abaixo da EMA 50
- OU RSI cai abaixo de rsi_min (perda de momentum, padrão 40)

#### Scenario: Sinal de Venda por Quebra de EMA 50
- DADO que há uma posição aberta
- E o preço cruza abaixo da EMA 50
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de venda (-1) é gerado

#### Scenario: Sinal de Venda por Perda de Momentum
- DADO que há uma posição aberta
- E o RSI cai abaixo de 40
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de venda (-1) é gerado

### Requirement: Otimização de Parâmetros EMA RSI Volume
A estratégia MUST suportar otimização de parâmetros via Grid Search.
Os parâmetros otimizáveis MUST incluir: ema_fast, ema_slow, rsi_period, rsi_min, rsi_max.
As faixas de otimização sugeridas MUST ser:
- ema_fast: 20-100 (step 10)
- ema_slow: 100-300 (step 50)
- rsi_period: 10-20 (step 2)
- rsi_min: 30-45 (step 5)
- rsi_max: 45-60 (step 5)

#### Scenario: Otimizar Parâmetros EMA RSI Volume
- DADO que o usuário está na página de Parameter Optimization
- E seleciona a estratégia "EMA 50/200 + RSI + Volume"
- QUANDO o usuário configura ranges de otimização
- ENTÃO os parâmetros ema_fast, ema_slow, rsi_period, rsi_min, rsi_max são otimizáveis
- E as faixas sugeridas são pré-populadas

### Requirement: Compatibilidade com Stop Loss e Take Profit
A estratégia MUST funcionar corretamente com Stop Loss e Take Profit configurados.
Os sinais de venda da estratégia MUST ser independentes dos stop/take profit.

#### Scenario: Estratégia com Stop Loss
- DADO que a estratégia está configurada com stop_pct=2%
- QUANDO uma posição é aberta
- E o preço cai 2%
- ENTÃO a posição é fechada por Stop Loss
- E o sinal de venda da estratégia não interfere

### Requirement: Metadados de Estratégia no Backend
O backend SHALL incluir metadados completos para a estratégia EMA RSI Volume.
Os metadados MUST incluir: id, name, description, category, parameters.

#### Scenario: Resposta da API com Metadados
- DADO que o frontend solicita a lista de estratégias
- QUANDO a API responde
- ENTÃO a estratégia "EMA 50/200 + RSI + Volume" está incluída
- E contém id="emarsivolume", name="EMA 50/200 + RSI + Volume", category="Trend Following"
