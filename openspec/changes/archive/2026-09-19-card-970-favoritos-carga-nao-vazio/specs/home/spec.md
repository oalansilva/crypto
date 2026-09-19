## ADDED Requirements

### Requirement: Home favorites KPI distinguishes load error from empty catalog

The Início KPI that reads the favorites list SHALL keep error and empty as separate copies. This card does not redesign Home layout, KPIs, or flow.

#### Scenario: Favorites fetch fails on Home

- **WHEN** the Home favorites query errors
- **THEN** the KPI shows «não disponível» and «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

#### Scenario: Home has no favorite after a successful fetch

- **WHEN** the Home favorites query succeeds
- **AND** there is no favorite to feature
- **THEN** the KPI MAY show «Nenhuma estratégia favoritada»
