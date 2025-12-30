# Especificação: Estratégias RSI Reversal e Bollinger Bands

## ADDED Requirements

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
