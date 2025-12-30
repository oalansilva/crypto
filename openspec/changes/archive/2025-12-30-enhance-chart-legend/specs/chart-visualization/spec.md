# Especificação: Configuração de Parâmetros e Legenda de Gráfico

## ADDED Requirements

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
