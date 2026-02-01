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

### Requirement: Auto Backtest Orchestration
The System SHALL provide an automated end-to-end backtest workflow that executes timeframe selection, parameter optimization, and risk management optimization sequentially without user intervention.
The System MUST return the final optimized configuration and automatically save it to the user's favorites with a timestamp note.

#### Scenario: User runs auto backtest for BTC/USDT with RSI
Given the user selects symbol "BTC/USDT" and strategy "RSI"
When the user triggers the auto backtest endpoint
Then the System SHALL:
1. Execute timeframe optimization across all default timeframes
2. Select the best timeframe based on Sharpe Ratio
3. Execute parameter grid search on the selected timeframe
4. Select the best parameter combination
5. Execute stop-loss/take-profit optimization
6. Select the best risk configuration
7. Save the final configuration to favorites with note "Auto-selected on [DATE]"
And return the run_id and status to the user

#### Scenario: Progress tracking during auto backtest
Given an auto backtest is running
When the user queries the status endpoint
Then the System MUST return:
- Current stage (1/3, 2/3, or 3/3)
- Stage description ("Optimizing timeframes", "Optimizing parameters", "Optimizing risk")
- Progress percentage (e.g., 33%, 66%, 100%)

### Requirement: Stage Result Logging
The System SHALL persist detailed logs of each optimization stage to `backend/full_execution_log.txt` using the existing logging format.
Each stage log MUST include timestamps, stage identifier, and key results.

### Requirement: Error Handling and Recovery (Auto Backtest)
The System SHALL gracefully handle failures at any optimization stage and provide clear error feedback to the user.
The System MUST save partial logs when a stage fails for debugging purposes.

### Requirement: Process Cancellation (Auto Backtest)
The System SHALL allow users to cancel a running auto backtest at any time.

### Requirement: Input Validation (Auto Backtest)
The System SHALL validate user inputs before starting the auto backtest workflow.

### Requirement: Execution History (Auto Backtest)
The System SHALL persist all auto backtest executions and allow users to view past runs.

### Requirement: Default Configuration Values (Auto Backtest)
The System SHALL use consistent default values for fee and slippage across all auto backtest executions.

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
