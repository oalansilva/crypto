## ADDED Requirements

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
