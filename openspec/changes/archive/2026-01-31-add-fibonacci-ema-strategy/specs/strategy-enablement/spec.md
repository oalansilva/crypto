# strategy-enablement Specification Delta

## ADDED Requirements

### Requirement: Habilitar Estratégia Fibonacci + EMA 200
O formulário Custom Backtest SHALL permitir selecionar a estratégia "Fibonacci (0.5 / 0.618) + EMA 200".
A estratégia MUST estar habilitada (não desabilitada) para seleção.
A estratégia MUST ser identificada pelo ID "fibonacciema".

#### Scenario: Selecionar Fibonacci EMA Strategy
- DADO que o usuário está no formulário Custom Backtest
- QUANDO o usuário seleciona a estratégia "Fibonacci (0.5 / 0.618) + EMA 200"
- ENTÃO a estratégia é selecionada
- E campos de parâmetros específicos para a estratégia aparecem dinamicamente

### Requirement: Configuração de Parâmetros Fibonacci EMA
O formulário SHALL exibir campos para configurar parâmetros da estratégia Fibonacci EMA.
Os campos MUST incluir: EMA Period, Swing Lookback, Fib Level 1, Fib Level 2, Level Tolerance.
Os valores padrão MUST ser: ema_period=200, swing_lookback=20, fib_level_1=0.5, fib_level_2=0.618, level_tolerance=0.005.

#### Scenario: Configurar Parâmetros Fibonacci EMA
- DADO que "Fibonacci (0.5 / 0.618) + EMA 200" está selecionada
- QUANDO o usuário visualiza o formulário
- ENTÃO campos "EMA Period", "Swing Lookback", "Fib Level 1", "Fib Level 2", "Level Tolerance" são exibidos
- E os valores padrão são 200, 20, 0.5, 0.618, 0.005 respectivamente

### Requirement: Detecção de Swing High/Low
A estratégia MUST detectar swing highs e swing lows automaticamente.
A detecção MUST usar uma janela de lookback configurável (padrão: 20 barras).
Um swing high MUST ser um pico local onde o preço é maior que N barras antes e depois.
Um swing low MUST ser um vale local onde o preço é menor que N barras antes e depois.

#### Scenario: Detectar Swing High
- DADO que há dados históricos suficientes (>= swing_lookback * 2)
- QUANDO a estratégia analisa os dados
- ENTÃO swing highs são identificados como picos locais
- E cada swing high é validado como não quebrado por barras subsequentes

#### Scenario: Detectar Swing Low
- DADO que há dados históricos suficientes
- QUANDO a estratégia analisa os dados
- ENTÃO swing lows são identificados como vales locais
- E cada swing low é validado como não quebrado por barras subsequentes

### Requirement: Cálculo de Níveis de Fibonacci
A estratégia MUST calcular níveis de retração de Fibonacci entre swing high e swing low mais recentes.
Os níveis MUST incluir 0.5 (50%) e 0.618 (golden ratio).
O cálculo MUST ser: fib_level = swing_low + (swing_high - swing_low) * ratio.

#### Scenario: Calcular Fibonacci 0.5
- DADO que swing_high = 50000 e swing_low = 40000
- QUANDO a estratégia calcula Fibonacci 0.5
- ENTÃO fib_0.5 = 40000 + (50000 - 40000) * 0.5 = 45000

#### Scenario: Calcular Fibonacci 0.618
- DADO que swing_high = 50000 e swing_low = 40000
- QUANDO a estratégia calcula Fibonacci 0.618
- ENTÃO fib_0.618 = 40000 + (50000 - 40000) * 0.618 = 46180

### Requirement: Lógica de Compra Fibonacci EMA
A estratégia MUST gerar sinal de compra quando TODAS as condições são atendidas:
- Preço está acima da EMA 200 (filtro de tendência de alta)
- Preço está dentro da tolerância de um nível Fibonacci (0.5 ou 0.618)
- Preço mostra confirmação de bounce (reversão do movimento de queda)

#### Scenario: Sinal de Compra em Fibonacci 0.5
- DADO que o preço está acima da EMA 200
- E o preço está em 45000 (dentro de 0.5% do Fibonacci 0.5 = 45000)
- E o preço mostra bounce (close > open após tocar o nível)
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de compra (1) é gerado

#### Scenario: Sinal de Compra em Fibonacci 0.618
- DADO que o preço está acima da EMA 200
- E o preço está em 46200 (dentro de 0.5% do Fibonacci 0.618 = 46180)
- E o preço mostra bounce
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de compra (1) é gerado

#### Scenario: Sinal de Compra Bloqueado por Tendência de Baixa
- DADO que o preço está abaixo da EMA 200
- E o preço toca Fibonacci 0.618
- E o preço mostra bounce
- QUANDO a estratégia avalia o sinal
- ENTÃO NENHUM sinal de compra é gerado (filtro de tendência bloqueia)

### Requirement: Lógica de Venda Fibonacci EMA
A estratégia MUST gerar sinal de venda quando QUALQUER condição é atendida:
- Preço cruza abaixo da EMA 200 (reversão de tendência)
- OU preço atinge swing high (alvo de lucro - resistência)

#### Scenario: Sinal de Venda por Quebra de EMA 200
- DADO que há uma posição aberta
- E o preço cruza abaixo da EMA 200
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de venda (-1) é gerado

#### Scenario: Sinal de Venda por Atingir Swing High
- DADO que há uma posição aberta
- E o preço atinge ou supera o swing high (50000)
- QUANDO a estratégia avalia o sinal
- ENTÃO um sinal de venda (-1) é gerado (take profit)

### Requirement: Tolerância de Nível Fibonacci
A estratégia MUST usar uma tolerância configurável para detectar quando o preço toca um nível Fibonacci.
A tolerância padrão MUST ser 0.5% (0.005).
O preço é considerado "no nível" se: abs(price - fib_level) / price <= tolerance.

#### Scenario: Preço Dentro da Tolerância
- DADO que Fibonacci 0.5 = 45000
- E tolerância = 0.005 (0.5%)
- E preço = 45200
- QUANDO a estratégia verifica se preço está no nível
- ENTÃO abs(45200 - 45000) / 45200 = 0.0044 <= 0.005
- E o preço é considerado "no nível Fibonacci 0.5"

### Requirement: Otimização de Parâmetros Fibonacci EMA
A estratégia MUST suportar otimização de parâmetros via Grid Search.
Os parâmetros otimizáveis MUST incluir: ema_period, swing_lookback, fib_level_1, fib_level_2, level_tolerance.
As faixas de otimização sugeridas MUST ser:
- ema_period: 100-300 (step 50)
- swing_lookback: 10-40 (step 5)
- fib_level_1: 0.382-0.618 (step 0.05)
- fib_level_2: 0.5-0.786 (step 0.05)
- level_tolerance: 0.001-0.01 (step 0.001)

#### Scenario: Otimizar Parâmetros Fibonacci EMA
- DADO que o usuário está na página de Parameter Optimization
- E seleciona a estratégia "Fibonacci (0.5 / 0.618) + EMA 200"
- QUANDO o usuário configura ranges de otimização
- ENTÃO os parâmetros ema_period, swing_lookback, fib_level_1, fib_level_2, level_tolerance são otimizáveis
- E as faixas sugeridas são pré-populadas

### Requirement: Compatibilidade com Stop Loss e Take Profit
A estratégia MUST funcionar corretamente com Stop Loss e Take Profit configurados.
Os sinais de venda da estratégia MUST ser independentes dos stop/take profit.
O swing high MUST funcionar como take profit natural da estratégia.

#### Scenario: Estratégia com Stop Loss
- DADO que a estratégia está configurada com stop_pct=2%
- QUANDO uma posição é aberta em Fibonacci 0.618
- E o preço cai 2%
- ENTÃO a posição é fechada por Stop Loss
- E o sinal de venda da estratégia não interfere

### Requirement: Metadados de Estratégia no Backend
O backend SHALL incluir metadados completos para a estratégia Fibonacci EMA.
Os metadados MUST incluir: id, name, description, category, parameters.

#### Scenario: Resposta da API com Metadados
- DADO que o frontend solicita a lista de estratégias
- QUANDO a API responde
- ENTÃO a estratégia "Fibonacci (0.5 / 0.618) + EMA 200" está incluída
- E contém id="fibonacciema", name="Fibonacci (0.5 / 0.618) + EMA 200", category="Pullback"
