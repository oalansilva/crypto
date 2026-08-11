## ADDED Requirements

### Requirement: Indicadores persistem padrões gráficos detectados
The market indicator pipeline SHALL persist detected chart pattern events alongside indicator values.

#### Scenario: Padrões aparecem na leitura de indicadores
- **WHEN** `get_latest` or `get_time_series` reads market indicator rows
- **THEN** the returned rows SHALL include detected `chart_patterns` when available.

#### Scenario: Ausência de padrão não quebra consumidores
- **WHEN** no chart pattern is detected for a candle
- **THEN** the system SHALL return an empty list or nullable value that consumers can treat as no events.
