## ADDED Requirements

### Requirement: Favorites result parameter labels are trader-facing
Favorites result charts SHALL render visible strategy parameter labels and common parameter values in trader-facing Portuguese instead of raw internal keys and English values.

#### Scenario: Favorite result shows translated parameters
- **WHEN** a user opens a favorite analysis result with visible parameters including `direction`, `ema_short`, `sma_medium`, `sma_long`, `stop_loss`, and `data_source`
- **THEN** the result configuration SHALL show Portuguese labels such as `Direção`, `EMA curta`, `SMA média`, `SMA longa`, `Stop de perda`, and `Fonte de dados`
- **AND** common values SHALL be shown as trader-facing values such as `Compra` and `CCXT`
- **AND** raw labels such as `direction`, `ema short`, `sma medium`, `sma long`, `stop loss`, and `data source` SHALL NOT appear in that configuration block

#### Scenario: Protected favorite result keeps parameters hidden
- **WHEN** a common user opens a protected favorite result
- **THEN** technical parameters SHALL remain hidden behind the protected-parameters message
