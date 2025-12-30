# backend Specification

## Purpose
TBD - created by archiving change generic-indicators-dynamic-params. Update Purpose after archive.
## Requirements
### Requirement: Introspecção de Indicadores
O sistema SHALL fornecer um catálogo completo de indicadores suportados pela biblioteca `pandas-ta`.
Para cada indicador, o sistema MUST retornar:
- Identificador (ex: `rsi`, `bbands`)
- Nome legível / Categoria
- Lista de parâmetros aceitos com seus tipos (int, float) e valores padrão.

### Requirement: Execução Dinâmica
O motor de backtest SHALL aceitar uma definição abstrata de estratégia contendo:
- Lista de indicadores a serem calculados.
- Condições lógicas de Entrada (Long/Short).
- Condições lógicas de Saída.
O sistema NÃO DEVE depender de classes de estratégia hardcoded (como `SMACrossStrategy`) para novos testes.

#### Scenario: Executar Estratégia Desconhecida
- DADO que o front envia uma estratégia usando o indicador "Keltner Channels"
- MESMO QUE não exista uma classe `KeltnerStrategy` no código
- O sistema DEVE calcular os canais usando `pandas-ta` e executar as ordens baseadas nas condições fornecidas.

### Requirement: Comparação Multi-Estratégia
O endpoint de backtest SHALL aceitar uma lista de configurações de estratégia.
O retorno DEVE agrupar os resultados por estratégia para permitir comparação direta de métricas (Sharpe, Retorno, Drawdown).

