## ADDED Requirements

### Requirement: Short period window still starts

A short evaluation window (15 dias, or 1 mês with timeframe 1d) SHALL NOT block Preflight or start. Combinations that lack enough sample SHALL still appear with the existing seal `Amostra insuficiente`. The listing-gate and eligibility policy already in this spec SHALL remain; this requirement SHALL NOT add a new sample threshold.

#### Scenario: Fifteen days with 1d can start

- **WHEN** the operator selects 15 dias and 1d and otherwise valid axes, then starts the sweep
- **THEN** start is not blocked because the window is short
- **AND** rows without enough sample show the seal `Amostra insuficiente`

#### Scenario: One month with 1d can start

- **WHEN** the operator selects 1 mês and 1d and otherwise valid axes, then starts the sweep
- **THEN** start is not blocked because the window is short
- **AND** rows without enough sample show the seal `Amostra insuficiente`
