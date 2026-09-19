## ADDED Requirements

### Requirement: Home KPI does not show a false favorites load error during renewal

On Início (`/home`), during access renewal, the favorites KPI SHALL show the featured strategy when the catalog is on the server. The KPI MUST NOT show «Não foi possível carregar `/api/favorites`.» in that window. A real favorites fetch failure outside renewal continues the existing error copy. This card SHALL NOT redesign Home layout, KPIs, or flow.

#### Scenario: Renewal window shows the featured strategy

- **WHEN** the operator opens `/home`
- **AND** crypto favorites are stored
- **AND** access is being renewed
- **THEN** the «Melhor estratégia (7d)» KPI shows the strategy
- **AND** MUST NOT show «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

#### Scenario: Real Home favorites failure keeps the existing error copy

- **WHEN** the Home favorites query fails by real network error or invalid body
- **AND** the session is not dead
- **THEN** the KPI shows «não disponível» and «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»
