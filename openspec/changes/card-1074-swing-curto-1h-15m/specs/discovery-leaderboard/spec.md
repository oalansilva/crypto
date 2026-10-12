## ADDED Requirements

### Requirement: Discovery cost label shows real fee and timeframe slippage

Persisted Discovery `fees_slippage` SHALL record the trading fee 0,075% per side and the slippage actually used for that result's timeframe (0,02% on 1d and 4h; 0,03% on 1h; 0,05% on 15m). The visible evidence line SHALL show `taxa 0,075%` and that slippage. It SHALL NOT show 0,1% fee with 0,1% slippage unless those were the values used.

Selo, ranking, eligibility (≥30 trades, ≥90% coverage) and Promover SHALL stay the Discovery rules already specified. Combo GO/NO-GO SHALL NOT veto a Discovery row.

#### Scenario: 1h row shows 0,075% fee and 0,03% slippage

- **WHEN** a 1h Discovery result is shown on Decidir
- **THEN** the evidence line includes taxa 0,075% and slippage 0,03%

#### Scenario: 15m row shows 0,05% slippage

- **WHEN** a 15m Discovery result is shown on Decidir
- **THEN** the evidence line includes taxa 0,075% and slippage 0,05%

#### Scenario: 4h and 1d rows show 0,02% slippage

- **WHEN** a 4h or 1d Discovery result is shown
- **THEN** the evidence line includes taxa 0,075% and slippage 0,02%
- **AND** the label is not 0,1% / 0,1%
