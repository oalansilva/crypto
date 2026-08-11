# Market Indicators Specification

## Purpose

Provide deterministic and incremental calculation of EMA, SMA, RSI and MACD across supported timeframes, persist indicator vectors in a dedicated table, and validate computed values against TradingView references.
## Requirements
### Requirement: Indicadores usam TA-Lib como engine padrão

The system SHALL use `TA-Lib` as the default runtime engine for EMA, SMA, RSI and MACD calculations.

#### Scenario: Motor padrão em produção
- **GIVEN** uma execução da pipeline de indicadores
- **WHEN** calculando EMA/SMA/RSI/MACD
- **THEN** a implementação SHALL utilizar chamadas de TA-Lib.
- **AND** `pandas-ta` não deverá ser parte do fluxo de produção/recálculo desta change.

### Requirement: Sistema calcula EMA e SMA em todos os timeframes ativos

The system SHALL compute EMA and SMA values for each configured symbol/timeframe pair.

#### Scenario: Indicadores base gerados por timeframe
- **GIVEN** a tabela de candles possui novo candle fechado para `symbol`/`timeframe`
- **WHEN** o pipeline de indicadores roda
- **THEN** os campos abaixo deverão ser persistidos em `market_indicator`:
  - `ema_9`, `ema_21`, `sma_20`, `sma_50`
- **AND** com `ts` igual ao timestamp do candle de fechamento processado.

### Requirement: Sistema calcula RSI e MACD em todos os timeframes ativos

The system SHALL compute RSI 14 and MACD (12,26,9) for each configured symbol/timeframe pair.

#### Scenario: Indicadores osciladores persistidos
- **GIVEN** candles fechados para `symbol`/`timeframe`
- **WHEN** o pipeline de indicadores roda
- **THEN** os campos abaixo deverão ser persistidos:
  - `rsi_14`, `macd_line`, `macd_signal`, `macd_histogram`
- **AND** manter valores nulos durante a fase de aquecimento (`min_periods` não atingida).

### Requirement: Pipeline incremental e idempotente

The system SHALL update indicators incrementally and safely on retries/replays.

#### Scenario: Nova vela atualiza só janela recente
- **GIVEN** um novo candle chega para `symbol`/`timeframe`
- **WHEN** o job roda
- **THEN** apenas janela mínima necessária será recalculada (até `max_lookback` barras para trás)
- **AND** registros já existentes de timestamps não devem duplicar.

#### Scenario: Reprocesso após correção
- **GIVEN** reprocessamento de últimas N velas é solicitado
- **WHEN** pipeline roda para aquela janela
- **THEN** os valores já existentes do período alvo são sobrescritos
- **AND** o restante da série permanece consistente.

### Requirement: Persistência dedicada com metadados e integridade

The system SHALL store indicators in dedicated storage.

#### Scenario: Unicidade e rastreabilidade
- **GIVEN** um registro técnico para `symbol`, `timeframe`, `ts`
- **WHEN** é persistido
- **THEN** a chave `(symbol, timeframe, ts)` será única
- **AND** os metadados incluem `source`, `provider`, `updated_at`, `is_recomputed`, `row_count`.

### Requirement: Validação contra TradingView

The system SHALL include automated checks against TradingView reference outputs.

#### Scenario: Comparação de referência
- **GIVEN** fixture de preços e indicadores calculados pela TradingView
- **WHEN** testes de validação executam
- **THEN** os valores devem bater com tolerância definida por indicador.

### Requirement: Interface de leitura de indicadores para scoring

The scoring subsystem SHALL read indicator values from the dedicated store.

#### Scenario: Scoring sem recálculo inline
- **GIVEN** um run de scoring
- **WHEN** precisar de features técnicas
- **THEN** os valores devem vir de `market_indicator`
- **AND** o scoring não deve recalcular indicadores em linha.

### Requirement: Sistema calcula indicadores avançados em todos os timeframes ativos

The system SHALL compute Bollinger Bands, ATR, Stochastic, OBV, and Ichimoku values for each configured `symbol`/`timeframe` pair processed by the dedicated market indicator pipeline.

#### Scenario: Indicadores avançados gerados por candle fechado

- **GIVEN** candles OHLCV fechados para um `symbol`/`timeframe` ativo
- **WHEN** o pipeline dedicado de indicadores roda
- **THEN** o sistema SHALL calcular Bollinger Bands, ATR, Stochastic, OBV e Ichimoku para cada candle elegível
- **AND** valores SHALL permanecer nulos durante a fase de aquecimento quando a janela mínima ainda não existir

#### Scenario: Indicadores avançados disponíveis para scoring

- **GIVEN** um run de scoring precisa de features técnicas avançadas
- **WHEN** o scoring lê indicadores técnicos
- **THEN** o sistema SHALL ler Bollinger Bands, ATR, Stochastic, OBV e Ichimoku do armazenamento dedicado de indicadores
- **AND** o scoring MUST NOT recalcular esses indicadores em linha

### Requirement: Sistema persiste indicadores avançados com integridade e metadados

The system SHALL persist advanced indicator values in the dedicated market indicator storage while preserving uniqueness by `symbol`, `timeframe`, and candle timestamp.

#### Scenario: Persistência idempotente de indicadores avançados

- **GIVEN** um registro técnico para `symbol`, `timeframe` e `ts`
- **WHEN** indicadores avançados são persistidos
- **THEN** o sistema SHALL armazenar os valores avançados no mesmo registro lógico do candle
- **AND** retries/replays MUST update the existing row instead of creating duplicates
- **AND** metadata such as `provider`, `source_window`, `row_count`, `is_recomputed`, and `updated_at` MUST remain populated

#### Scenario: Recompute incremental preserva consistência

- **GIVEN** indicadores avançados já persistidos para um `symbol`/`timeframe`
- **WHEN** um novo candle chega e o recompute incremental roda
- **THEN** o sistema SHALL recalculate only the required lookback window for all basic and advanced indicators
- **AND** rows outside the recompute window MUST remain unchanged

### Requirement: Fórmulas de indicadores avançados são documentadas

The system SHALL document the formulas, default parameters, and displacement semantics used for each advanced indicator.

#### Scenario: Fórmulas disponíveis para revisão técnica

- **WHEN** um reviewer consulta a documentação da change
- **THEN** ela MUST define Bollinger Bands as SMA plus/minus standard-deviation bands
- **AND** ATR as Wilder-style average true range over true range values
- **AND** Stochastic as close position within the rolling high-low range plus `%K`/`%D` smoothing
- **AND** OBV as cumulative volume adjusted by close direction
- **AND** Ichimoku as Tenkan, Kijun, Senkou A, Senkou B, and Chikou using highest-high/lowest-low windows and documented displacement

### Requirement: Indicadores avançados usam parâmetros padrão explícitos

The system SHALL use explicit default parameters for advanced indicators unless a later capability introduces configurable indicator parameter sets.

#### Scenario: Parâmetros padrão aplicados no runtime

- **WHEN** o pipeline calcula indicadores avançados sem parâmetros customizados
- **THEN** Bollinger Bands MUST use length 20 and standard deviation multiplier 2
- **AND** ATR MUST use length 14
- **AND** Stochastic MUST use fast `%K` length 14, `%K` smoothing 3, and `%D` smoothing 3
- **AND** Ichimoku MUST use Tenkan 9, Kijun 26, Senkou Span B 52, and displacement 26
- **AND** OBV MUST use close and volume without a lookback period

### Requirement: Validação cruzada usa três fontes de referência

The system SHALL include automated validation evidence for advanced indicator calculations using three independent reference sources where applicable.

#### Scenario: Uso de fixtures TradingView como base de validação

- **GIVEN** fixtures OHLCV exportados da TradingView
- **WHEN** testes de paridade executam
- **THEN** the system SHALL use those candles as reference market input for advanced indicator validation
- **AND** existing TradingView basic indicator reference columns MUST continue to pass within indicator-specific tolerances

#### Scenario: Paridade com TA-Lib para indicadores suportados

- **GIVEN** the runtime has TA-Lib available
- **WHEN** tests compare supported advanced indicators against TA-Lib calculations
- **THEN** Bollinger Bands, ATR, Stochastic, and OBV SHALL match TA-Lib outputs within indicator-specific tolerances
- **AND** Ichimoku MUST be excluded from TA-Lib parity because TA-Lib does not provide an Ichimoku function

#### Scenario: Paridade com pandas-ta para indicadores suportados

- **GIVEN** the runtime has pandas-ta available in the test environment
- **WHEN** tests compare supported advanced indicators against pandas-ta calculations
- **THEN** Bollinger Bands, ATR, Stochastic, and OBV SHALL match pandas-ta outputs within indicator-specific tolerances
- **AND** Ichimoku MUST be treated separately because chart displacement conventions differ from source-candle-aligned storage

#### Scenario: Paridade com implementação independente de fórmulas

- **GIVEN** an independent formula implementation in tests
- **WHEN** tests compare runtime output with documented formulas
- **THEN** Bollinger Bands, ATR, Stochastic, OBV, and Ichimoku SHALL match the independent formula outputs within indicator-specific tolerances

### Requirement: Ichimoku usa fórmulas corretas de midpoint

The system SHALL calculate Ichimoku lines using rolling highest-high and lowest-low midpoints, not independent high-only or low-only rolling values.

#### Scenario: Cálculo correto de Tenkan e Kijun

- **WHEN** Ichimoku is calculated for a candle with enough history
- **THEN** Tenkan MUST equal `(highest_high_9 + lowest_low_9) / 2`
- **AND** Kijun MUST equal `(highest_high_26 + lowest_low_26) / 2`

#### Scenario: Cálculo correto de spans e Chikou

- **WHEN** Ichimoku spans are calculated for a candle with enough history
- **THEN** Senkou Span A MUST equal `(Tenkan + Kijun) / 2`
- **AND** Senkou Span B MUST equal `(highest_high_52 + lowest_low_52) / 2`
- **AND** Chikou MUST represent the close series with the documented 26-period lagging displacement
- **AND** persisted values MUST document whether displacement is represented as metadata or shifted timestamps

### Requirement: Sistema calcula suporte e resistência por pivot clássico
The market indicator pipeline SHALL calculate classic pivot point support and resistance levels for each processed `symbol`/`timeframe` candle.

#### Scenario: Níveis S1-S3 e R1-R3 calculados
- **WHEN** the market indicator pipeline processes a candle with a previous candle in the same timeframe
- **THEN** it SHALL calculate `pivot_point`, `support_1`, `support_2`, `support_3`, `resistance_1`, `resistance_2`, and `resistance_3` from the previous candle OHLC values.

### Requirement: Primeiro candle sem contexto mantém níveis nulos
The market indicator pipeline SHALL keep pivot support/resistance values null when no previous candle is available.

#### Scenario: Warmup sem candle anterior
- **WHEN** the first candle in a processed series has no previous candle
- **THEN** all pivot support/resistance fields for that row SHALL be null.

### Requirement: Níveis são persistidos e retornados por timeframe
The system SHALL persist and return pivot support/resistance levels in the dedicated market indicator store.

#### Scenario: Leitura de indicadores inclui suporte/resistência
- **WHEN** `get_latest` or `get_time_series` reads market indicator rows for a symbol/timeframe
- **THEN** the returned rows SHALL include `pivot_point`, `support_1`, `support_2`, `support_3`, `resistance_1`, `resistance_2`, and `resistance_3`.

#### Scenario: Atualização por timeframe processado
- **WHEN** indicator recompute runs for a specific timeframe
- **THEN** pivot support/resistance levels SHALL be updated for candles in that timeframe without requiring other timeframes to run.

### Requirement: Indicadores persistem padrões gráficos detectados
The market indicator pipeline SHALL persist detected chart pattern events alongside indicator values.

#### Scenario: Padrões aparecem na leitura de indicadores
- **WHEN** `get_latest` or `get_time_series` reads market indicator rows
- **THEN** the returned rows SHALL include detected `chart_patterns` when available.

#### Scenario: Ausência de padrão não quebra consumidores
- **WHEN** no chart pattern is detected for a candle
- **THEN** the system SHALL return an empty list or nullable value that consumers can treat as no events.

### Requirement: Indicadores possuem score normalizado para engine composto
The scoring subsystem SHALL convert persisted technical indicator values into normalized scores from `0` to `10`.

#### Scenario: Score tecnico dentro da faixa contratada
- **GIVEN** a persisted `market_indicator` row with all inputs required by the active ruleset
- **WHEN** the indicator scoring service scores the row
- **THEN** every emitted indicator score SHALL be greater than or equal to `0`
- **AND** less than or equal to `10`.

### Requirement: Regras de score sao configuraveis por indicador
The indicator scoring subsystem SHALL load per-indicator scoring rules from configuration.

#### Scenario: Ruleset padrao carregado
- **WHEN** the scoring service starts without an override path
- **THEN** it SHALL load the default versioned JSON ruleset from backend configuration.

#### Scenario: Ruleset alternativo carregado
- **GIVEN** `INDICATOR_SCORE_RULES_PATH` points to a valid ruleset JSON file
- **WHEN** the scoring service loads rules
- **THEN** it SHALL use that file instead of the default ruleset.

### Requirement: Scores carregam versao das regras
The indicator scoring subsystem SHALL include the active scoring ruleset version in each emitted score.

#### Scenario: Versao propagada no resultado
- **GIVEN** an active ruleset with version `technical-normalization/v1`
- **WHEN** the scoring service emits indicator scores
- **THEN** each score SHALL include `rule_version` equal to `technical-normalization/v1`.

### Requirement: Benchmark de normalizacao documentado
The system SHALL document how to benchmark indicator score normalization.

#### Scenario: Benchmark reproduzivel
- **WHEN** an engineer needs to measure normalization throughput
- **THEN** the OpenSpec change SHALL document the benchmark command, method, and acceptance target.

## Data model

- Add/modify `market_indicator` table:
  - `symbol` (string, not null)
  - `timeframe` (string, not null)
  - `ts` (timestamp with tz, not null)
  - `ema_9`, `ema_21`, `sma_20`, `sma_50`, `rsi_14`, `macd_line`, `macd_signal`, `macd_histogram` (numeric)
  - `is_recomputed` (boolean)
  - `source` (enum/string)
  - `provider` (string)
  - `source_window` (json)
  - `row_count` (int)
  - `updated_at` (timestamp with tz)
- Unique constraint on `(symbol, timeframe, ts)`.
- `provider` deve ser gravado como `talib` para este padrão de execução.

## API / Contract

### Backend endpoint

### `POST /api/admin/indicators/recompute`
- Request: `{"symbol": "BTCUSDT", "timeframes": ["1m","5m","15m","1h","4h","1d"], "force_full": false}`
- Response success: `{"status":"accepted","job_id":"...","estimated_bars":1234}`
- Response error: `409` se recompute já em execução para símbolo/timeframe; `400` se parâmetros inválidos.

## Acceptance criteria

- Indicadores EMA/SMA/RSI/MACD persistidos em tabela dedicada para todos os timeframes alvo.
- Recompute incremental funcional, sem necessidade de recalcular série completa em tick regular.
- Chave única `(symbol, timeframe, ts)` garantida no banco.
- Testes automáticos de referência TradingView com tolerância definida e pass.
- Scoring consome `market_indicator` sem recálculo inline.
- `talib` é o único engine de runtime da trilha da change.
