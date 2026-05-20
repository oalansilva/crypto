## MODIFIED Requirements

### Requirement: Armazenar Métricas Compostas
O sistema SHALL armazenar `total_return` como Retorno Composto ao salvar nos Favoritos. O painel de Favoritos SHALL exibir o mesmo retorno composto, não soma simples. O sistema MUST preserve `total_return_pct` and `total_pnl_pct` as percentage-point values from the backend and MUST NOT multiply those fields by 100 again when persisting or rendering Favorites metrics.

#### Scenario: Compound return stored and displayed
- **WHEN** the user saves a combo strategy to favorites
- **THEN** the system SHALL store `total_return` as the compound return
- **AND** the Favorites panel SHALL display the compound return, not a simple sum

#### Scenario: Backend percentage is not multiplied twice
- **WHEN** a favorite metric payload contains `total_return_pct=42`
- **THEN** the Favorites page MUST render the return as `+42.00%`
- **AND** the save flow MUST NOT persist the same value as `4200`

#### Scenario: Ratio metrics still render as percentages
- **WHEN** a favorite metric payload contains ratio fields such as `win_rate=0.6`, `max_drawdown=0.11`, or `total_return=0.42`
- **THEN** the Favorites page MUST render those values as `60.00%`, `11.00%`, and `+42.00%` respectively
