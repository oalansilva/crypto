# favorites-load-states Specification

## Purpose
TBD - created by archiving change card-970-favoritos-carga-nao-vazio. Update Purpose after archive.
## Requirements
### Requirement: Favorites load states are distinct

`/favorites` SHALL treat loading, successful list, load error, filter-empty, catalog-empty, and dead session as distinct operator-visible states. «Carregando estratégias...» SHALL last only while the list request runs and SHALL end in the list or in an explicit load error — never in the catalog-empty copy after a failed load.

#### Scenario: Happy path lists saved crypto pairs

- **WHEN** the session is valid
- **AND** crypto favorites (symbol containing `/`) are stored
- **AND** the operator opens `/favorites` with filters Todos and empty search
- **THEN** the grade lists those crypto pairs
- **AND** the screen MUST NOT show «Nenhuma estratégia favorita encontrada»
- **AND** the screen MUST NOT show «0 estratégias carregadas» as the only result

#### Scenario: Load error stays on Favoritos with retry

- **WHEN** the list request fails by network error, non-OK status after a still-valid session, invalid body, or failed parse
- **THEN** the operator sees an explicit load error
- **AND** sees an action «Tentar de novo»
- **AND** remains on `/favorites`
- **AND** MUST NOT be sent to `/login`
- **AND** MUST NOT see «Nenhuma estratégia favorita encontrada»

#### Scenario: Filter hides every crypto pair

- **WHEN** crypto pairs exist in the loaded catalog
- **AND** search or a filter (par, estratégia, tempo, estrela, direção) hides all of them
- **THEN** the screen says «Não há resultado com estes filtros.»
- **AND** MUST NOT use «Nenhuma estratégia favorita encontrada»

#### Scenario: Catalog is truly empty

- **WHEN** the list loaded successfully
- **AND** there is no crypto pair
- **AND** filters are Todos and search is empty
- **THEN** the screen MAY show «Nenhuma estratégia favorita encontrada»

#### Scenario: Dead session goes to login

- **WHEN** the session is dead
- **THEN** the operator is sent to login
- **AND** MUST NOT remain on a fake empty Favorites grade

#### Scenario: Analysis still has candles and trades

- **WHEN** the operator opens the chart or analysis of a favorite after this change
- **THEN** candles and trades remain available
- **AND** this card SHALL NOT remove analysis history; it SHALL remove that history from the grade payload

### Requirement: Home and Monitor do not treat list failure as empty catalog

Any surface where the operator sees the favorites list (Favoritos, Início `/home`, Monitor `/monitor`) SHALL show a load failure as a load failure. Failure MUST NOT appear as «não há estratégias» / catalog empty.

#### Scenario: Home KPI on favorites fetch error

- **WHEN** `/home` fails to load `/api/favorites`
- **THEN** the KPI shows that the load failed (existing copy «Não foi possível carregar `/api/favorites`.»)
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

#### Scenario: Monitor first load failure

- **WHEN** `/monitor` fails to load the favorites-derived list
- **THEN** the operator sees that the load failed
- **AND** MUST NOT see «Nenhum ativo disponível no monitor» as if the catalog were empty

