# chart-visualization Specification

## Purpose
TBD - created by archiving change enhance-chart-legend. Update Purpose after archive.
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

### Requirement: Visualização de RSI em Painel Separado
O gráfico SHALL exibir RSI em painel inferior (lower). RSI em roxo (#8b5cf6), legenda "RSI(14)" ou período configurado. Painel RSI MUST incluir linhas de referência em rsi_min e rsi_max.

### Requirement: Sincronização de Indicadores com Parâmetros
Os indicadores visualizados MUST refletir os parâmetros configurados (ema_fast, ema_slow, rsi_period). Backend MUST retornar metadados com name, color, data, panel ("main" para EMAs, "lower" para RSI).

### Requirement: Visualização Fibonacci EMA
O gráfico SHALL exibir EMA 200 e níveis Fibonacci (0.5, 0.618) quando a estratégia Fibonacci EMA é executada. Cores distintas para EMA e níveis.
