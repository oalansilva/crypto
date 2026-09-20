## MODIFIED Requirements

### Requirement: Monitor catalog-empty copy only when the session has no crypto favorites

`/monitor` SHALL show «Nenhum ativo disponível no monitor» only when this session has no crypto favorite (symbol containing `/`). A 200 empty opportunities list, a cache hit of `[]`, or an analysis that returned no rows while crypto favorites exist MUST NOT use that catalog-empty copy. Layout, KPIs, column set, and the default Na carteira vs Todos filter stay as they are; only this empty-vs-error treatment changes. The existing load-error copy MUST remain «Não foi possível carregar as estratégias.» with «A lista de favoritos não chegou. Isto não significa que não há estratégias.» A transient network cut of the authenticated list request, with a valid session, MUST NOT paint that load-error copy on the first failure; the board waits tens of seconds in «Carregando sinais...» and only a persistent failure uses the load-error copy.

#### Scenario: Empty opportunities with crypto favorites is load error

- **WHEN** the operator opens `/monitor`
- **AND** this session has crypto favorites
- **AND** `GET /opportunities/` succeeds with an empty list **or** the analysis did not return signals
- **THEN** the operator sees the existing load error
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: True catalog empty remains empty

- **WHEN** this session has no crypto favorite
- **AND** the opportunities request succeeds with no row to show
- **THEN** the existing empty catalog copy MAY appear

#### Scenario: HTTP fetch failure still uses load error

- **WHEN** the request that fills the board fails persistently after the wait of tens of seconds
- **AND** the session is not dead
- **THEN** the operator sees the existing load error
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: Transient cut is not the last word on the first failure

- **WHEN** the authenticated list request is cut on first attempt
- **AND** the session is valid
- **AND** crypto favorites are on the server
- **THEN** the board stays on «Carregando sinais...» instead of painting the load error on that first cut
- **AND** if the list arrives in the same opening, `table.signals` lists the pairs

#### Scenario: Favorites list contract is unchanged

- **WHEN** the operator opens `/favorites` after this change
- **THEN** crypto favorites already saved continue to list
- **AND** this card SHALL NOT reopen the lean-list contract of #970
