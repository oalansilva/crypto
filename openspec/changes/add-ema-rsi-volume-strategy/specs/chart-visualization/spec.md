# chart-visualization Specification Delta

## ADDED Requirements

### Requirement: Visualização de EMA 50 e EMA 200
O gráfico de resultados SHALL exibir as linhas EMA 50 e EMA 200 quando a estratégia EMA RSI Volume é executada.
A EMA 50 MUST ser exibida em cor laranja (#fb923c).
A EMA 200 MUST ser exibida em cor azul (#3b82f6).
As legendas MUST mostrar "EMA 50" e "EMA 200" com as cores correspondentes.

#### Scenario: Visualizar EMAs no Gráfico Principal
- DADO que um backtest com EMA RSI Volume foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO duas linhas representando EMA 50 (laranja) e EMA 200 (azul) são exibidas no painel principal
- E a legenda mostra "EMA 50" em laranja e "EMA 200" em azul

### Requirement: Visualização de RSI em Painel Separado
O gráfico de resultados SHALL exibir o indicador RSI em um painel separado (lower panel).
A linha RSI MUST ser exibida em cor roxa (#8b5cf6).
A legenda MUST mostrar "RSI(14)" (ou o período configurado).
O painel RSI MUST incluir linhas de referência em 40 e 50 (ou rsi_min e rsi_max configurados).

#### Scenario: Visualizar RSI no Painel Inferior
- DADO que um backtest com EMA RSI Volume foi executado
- QUANDO o usuário visualiza o gráfico de resultados
- ENTÃO uma linha roxa representando o RSI é exibida no painel inferior
- E a legenda mostra "RSI(14)" em roxo
- E linhas de referência horizontais são exibidas em 40 e 50

### Requirement: Sincronização de Indicadores com Parâmetros
Os indicadores visualizados MUST refletir os parâmetros configurados pelo usuário.
Se o usuário configurar ema_fast=30, a legenda MUST mostrar "EMA 30".
Se o usuário configurar rsi_period=10, a legenda MUST mostrar "RSI(10)".

#### Scenario: Visualizar Indicadores com Parâmetros Customizados
- DADO que um backtest foi executado com ema_fast=30, ema_slow=150, rsi_period=10
- QUANDO o usuário visualiza o gráfico
- ENTÃO a legenda mostra "EMA 30", "EMA 150", "RSI(10)"
- E os indicadores calculados usam os períodos corretos

### Requirement: Metadados de Indicadores para Visualização
O backend SHALL retornar metadados de indicadores na resposta do backtest.
Os metadados MUST incluir: name, color, data, panel.
O campo panel MUST ser "main" para EMAs e "lower" para RSI.

#### Scenario: Resposta da API com Indicadores
- DADO que um backtest com EMA RSI Volume foi executado
- QUANDO o frontend solicita os resultados
- ENTÃO a resposta inclui array de indicadores
- E cada indicador contém name, color, data, panel
- E EMA 50 tem panel="main", color="#fb923c"
- E EMA 200 tem panel="main", color="#3b82f6"
- E RSI tem panel="lower", color="#8b5cf6"
