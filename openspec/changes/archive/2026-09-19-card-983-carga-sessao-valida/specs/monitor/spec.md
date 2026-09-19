## ADDED Requirements

### Requirement: Monitor does not show a false favorites-list error during renewal

On `/monitor`, during access renewal, the board SHALL show the signals derived from saved favorites when those favorites are on the server. The screen MUST NOT show the false load error of the favorites list in that window. A real load failure continues the existing Monitor load-error copy. This card SHALL NOT redesign Status, Preço, Distância, 7d, Tags, Operar, Par / Estratégia, KPIs, or flow. `MonitorDashboardTab` remains unmounted.

#### Scenario: Renewal window shows Monitor signals

- **WHEN** the operator opens `/monitor`
- **AND** crypto favorites are stored
- **AND** access is being renewed
- **THEN** `table.signals` lists the pairs
- **AND** MUST NOT show «Não foi possível carregar as estratégias.»
- **AND** MUST NOT show «Nenhum ativo disponível no monitor»

#### Scenario: Real Monitor load failure keeps the existing error copy

- **WHEN** the request that fills the board fails by real network error or invalid body
- **AND** the session is not dead
- **THEN** the operator sees the existing load error
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»
