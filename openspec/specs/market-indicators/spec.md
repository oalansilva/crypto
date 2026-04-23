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
