## ADDED Requirements

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
