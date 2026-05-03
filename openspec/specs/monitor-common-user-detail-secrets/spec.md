# monitor-common-user-detail-secrets Specification

## Purpose
TBD - created by archiving change issue-120-remove-monitor-user-secrets. Update Purpose after archive.
## Requirements
### Requirement: Common user Monitor detail hides protected technical blocks
The Monitor SHALL NOT show protected strategy `Parâmetros`, `Indicadores`, technical action buttons, card-mode toggle, or alternate timeframe buttons in the expanded opportunity detail for common users.

#### Scenario: Common user expands protected Monitor opportunity
- **WHEN** a common user expands a protected Monitor opportunity
- **THEN** the expanded detail does not include a `Parâmetros` block
- **AND** the expanded detail does not include an `Indicadores` block
- **AND** the expanded detail does not include `Exportar`, `Reavaliar`, `Ver gráfico`, or `Confirmar gestão`
- **AND** the expanded detail does not include `Price`, `Strategy`, `15m`, `1h`, or `4h` controls
- **AND** the expanded detail shows only the strategy timeframe as the chart timeframe
- **AND** the expanded detail still shows public strategy context and operational status

### Requirement: Admin Monitor detail keeps technical blocks
The Monitor SHALL keep strategy `Parâmetros`, `Indicadores`, technical action buttons, card-mode toggle, and timeframe controls visible in the expanded opportunity detail for administrators.

#### Scenario: Admin expands Monitor opportunity
- **WHEN** an administrator expands a Monitor opportunity
- **THEN** the expanded detail includes the `Parâmetros` block
- **AND** the expanded detail includes the `Indicadores` block
- **AND** the expanded detail includes technical actions and timeframe controls

