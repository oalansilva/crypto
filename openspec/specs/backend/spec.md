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

#### Scenario: Catálogo retorna metadados de indicadores
- **GIVEN** o usuário consulta o endpoint de catálogo de indicadores
- **WHEN** o sistema responde com a lista disponível
- **THEN** cada indicador DEVE incluir identificador, nome/categoria e parâmetros
- **AND** os parâmetros DEVEM informar tipo e valor padrão

### Requirement: Execução Dinâmica
O motor de backtest SHALL aceitar uma definição abstrata de estratégia contendo:
- Lista de indicadores a serem calculados.
- Condições lógicas de Entrada (Long/Short).
- Condições lógicas de Saída.
O sistema NÃO DEVE depender de classes de estratégia hardcoded (como `SMACrossStrategy`) para novos testes.

#### Scenario: Executar Estratégia Desconhecida
- **GIVEN** o front envia uma estratégia usando o indicador "Keltner Channels"
- **AND** não existe uma classe `KeltnerStrategy` no código
- **WHEN** a execução é iniciada
- **THEN** o sistema DEVE calcular os canais usando `pandas-ta`
- **AND** DEVE executar as ordens baseadas nas condições fornecidas

### Requirement: Comparação Multi-Estratégia
O endpoint de backtest SHALL aceitar uma lista de configurações de estratégia.
O retorno DEVE agrupar os resultados por estratégia para permitir comparação direta de métricas (Sharpe, Retorno, Drawdown).

#### Scenario: Resultado agrupado por estratégia
- **GIVEN** o usuário envia múltiplas estratégias no mesmo request
- **WHEN** o backtest termina
- **THEN** a resposta DEVE agrupar métricas por estratégia
- **AND** cada grupo DEVE incluir Sharpe, Retorno e Drawdown

### Requirement: Auto Backtest Orchestration
The System SHALL provide an automated end-to-end backtest workflow that executes timeframe selection, parameter optimization, and risk management optimization sequentially without user intervention.
The System MUST return the final optimized configuration and automatically save it to the user's favorites with a timestamp note.

#### Scenario: Auto backtest executa etapas sequenciais
- **GIVEN** o usuário seleciona símbolo e estratégia
- **WHEN** dispara o endpoint de auto backtest
- **THEN** o sistema DEVE executar timeframe, parâmetros e risco em sequência
- **AND** DEVE salvar a configuração final nos favoritos com timestamp
- **AND** DEVE retornar `run_id` e status ao usuário

#### Scenario: Progress tracking during auto backtest
- **GIVEN** um auto backtest em execução
- **WHEN** o usuário consulta o endpoint de status
- **THEN** o sistema DEVE retornar o estágio atual (1/3, 2/3, 3/3)
- **AND** DEVE retornar a descrição do estágio
- **AND** DEVE retornar a porcentagem de progresso

### Requirement: Stage Result Logging
The System SHALL persist detailed logs of each optimization stage to `backend/full_execution_log.txt` using the existing logging format.
Each stage log MUST include timestamps, stage identifier, and key results.

#### Scenario: Logs por estágio são persistidos
- **GIVEN** um auto backtest em execução
- **WHEN** um estágio é concluído
- **THEN** o sistema DEVE registrar o estágio com timestamp e identificador
- **AND** DEVE persistir os principais resultados do estágio

### Requirement: Error Handling and Recovery (Auto Backtest)
The System SHALL gracefully handle failures at any optimization stage and provide clear error feedback to the user.
The System MUST save partial logs when a stage fails for debugging purposes.

#### Scenario: Falha em estágio retorna erro claro
- **GIVEN** um estágio falha durante o auto backtest
- **WHEN** o sistema detecta a falha
- **THEN** DEVE retornar erro claro ao usuário
- **AND** DEVE salvar logs parciais para debug

### Requirement: Process Cancellation (Auto Backtest)
The System SHALL allow users to cancel a running auto backtest at any time.

#### Scenario: Usuário cancela execução
- **GIVEN** um auto backtest em execução
- **WHEN** o usuário solicita cancelamento
- **THEN** o sistema DEVE interromper a execução
- **AND** DEVE atualizar o status para cancelado

### Requirement: Input Validation (Auto Backtest)
The System SHALL validate user inputs before starting the auto backtest workflow.

#### Scenario: Entrada inválida bloqueia execução
- **GIVEN** o usuário envia parâmetros inválidos
- **WHEN** o endpoint de auto backtest é acionado
- **THEN** o sistema DEVE recusar a execução
- **AND** DEVE retornar mensagem de validação

### Requirement: Execution History (Auto Backtest)
The System SHALL persist all auto backtest executions and allow users to view past runs.

#### Scenario: Histórico de execuções disponível
- **GIVEN** o usuário concluiu execuções anteriores
- **WHEN** consulta o histórico
- **THEN** o sistema DEVE listar execuções passadas
- **AND** DEVE incluir status e timestamps

### Requirement: Default Configuration Values (Auto Backtest)
The System SHALL use consistent default values for fee and slippage across all auto backtest executions.

#### Scenario: Valores padrão são aplicados
- **GIVEN** o usuário não informa fee/slippage
- **WHEN** o auto backtest inicia
- **THEN** o sistema DEVE aplicar valores padrão consistentes
- **AND** DEVE registrar esses valores no resultado

### Requirement: Intraday Execution Validation
The backtest engine SHALL validate trade execution using intraday data when precision mode is enabled.

#### Scenario: Stop loss hit before target (loss)
- **GIVEN** a long trade entered at $100,000 with stop at $98,500 and no explicit target
- **AND** the daily candle shows Low=$98,400, High=$105,000
- **WHEN** iterating through 1h candles for that day
- **AND** the 10:00 candle Low touches $98,400 (stop triggered)
- **THEN** exit the trade at $98,500 at 10:00
- **AND** ignore subsequent price action (even if it rallied to $105,000 later)

#### Scenario: Target hit before stop (win)
- **GIVEN** a long trade entered at $100,000 with target at $110,000 and stop at $98,500
- **AND** the daily candle shows Low=$98,400, High=$110,500
- **WHEN** iterating through 1h candles
- **AND** the 14:00 candle High reaches $110,000 first
- **THEN** exit the trade at $110,000 at 14:00
- **AND** ignore the later drop to $98,400

### Requirement: Precision Mode Configuration
The system SHALL accept a `precision_mode` parameter in backtest requests.

#### Scenario: Enable precise mode
- **WHEN** backtest request includes `{ "precision_mode": "precise", "intraday_timeframe": "1h" }`
- **THEN** use 1h data to validate execution
- **AND** return results with metadata: `{ "precision": "deep", "intraday_tf": "1h" }`

#### Scenario: Default to fast mode
- **WHEN** backtest request omits `precision_mode`
- **THEN** use daily-only execution (current behavior)
- **AND** return results with metadata: `{ "precision": "fast" }`