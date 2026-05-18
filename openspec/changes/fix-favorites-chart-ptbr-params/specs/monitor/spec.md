## ADDED Requirements

### Requirement: Monitor chart parameter labels are trader-facing
Monitor chart details SHALL render visible strategy parameter labels and common parameter values in trader-facing Portuguese instead of raw internal keys and English values.

#### Scenario: Monitor chart shows translated parameters
- **WHEN** a user opens a Monitor chart detail with visible parameters including `direction`, `ema_short`, `sma_medium`, `sma_long`, `stop_loss`, and `data_source`
- **THEN** the chart parameter section SHALL show Portuguese labels such as `Direção`, `EMA curta`, `SMA média`, `SMA longa`, `Stop de perda`, and `Fonte de dados`
- **AND** common values SHALL be shown as trader-facing values such as `Compra` and `CCXT`
- **AND** raw labels such as `direction`, `ema_short`, `sma_medium`, `sma_long`, `stop_loss`, and `data_source` SHALL NOT appear in that parameter section

#### Scenario: Protected monitor chart keeps parameters hidden
- **WHEN** a common user opens a protected Monitor chart
- **THEN** protected strategy parameters SHALL remain hidden
