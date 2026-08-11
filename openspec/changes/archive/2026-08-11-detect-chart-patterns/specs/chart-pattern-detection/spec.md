## ADDED Requirements

### Requirement: Sistema detecta padrões gráficos automáticos
The system SHALL detect golden cross, death cross, double top, and double bottom patterns for each processed `symbol`/`timeframe` candle.

#### Scenario: Padrões detectados no pipeline de indicadores
- **WHEN** the market indicator pipeline processes OHLCV rows for a symbol/timeframe
- **THEN** it SHALL evaluate golden cross, death cross, double top, and double bottom patterns using deterministic backend rules.

### Requirement: Eventos incluem confiança normalizada
Detected chart pattern events SHALL include a `confidence` score from 0 to 100.

#### Scenario: Confiança dentro do intervalo permitido
- **WHEN** a chart pattern event is emitted
- **THEN** its `confidence` value SHALL be greater than or equal to 0 and less than or equal to 100.

### Requirement: Eventos são persistidos com metadados
Detected chart pattern events SHALL be persisted with enough metadata for downstream consumers to inspect the rule that emitted the event.

#### Scenario: Evento persistido com metadados mínimos
- **WHEN** a chart pattern is persisted
- **THEN** the event SHALL include pattern name, direction, timestamp, reference price, confidence, source, dedupe key, and rule metadata.

### Requirement: Sistema deduplica padrões próximos
The system SHALL deduplicate repeated chart pattern events so the same pattern does not spam consumers across nearby candles.

#### Scenario: Eventos repetidos são deduplicados
- **WHEN** the same pattern/direction is detected repeatedly within the configured dedupe window
- **THEN** the persisted output SHALL keep only the first event for that window.
