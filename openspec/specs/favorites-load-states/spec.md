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

### Requirement: Session renewal with intact catalog lists favorites

During access renewal, `/favorites` SHALL list the saved crypto pairs when the catalog is on the server. The screen MUST NOT show the #970 load error («Não foi possível carregar as estratégias favoritas.» / «Carga falhou» / «Tentar de novo» with «a sessão continua válida») in that window. A 200 that arrived or will arrive MUST win over an abort or a transient 401. This card SHALL NOT undo #970: empty vs error vs filter stay distinct; the grade stays a lean list without candles.

#### Scenario: Renewal window lists saved crypto pairs

- **WHEN** the operator opens `/favorites` with filters Todos and empty search
- **AND** crypto favorites are stored
- **AND** `GET /api/favorites/` is 200 on the backend
- **AND** the access token is being renewed
- **THEN** the grade lists those crypto pairs
- **AND** MUST NOT show «Não foi possível carregar as estratégias favoritas.»
- **AND** MUST NOT show «Nenhuma estratégia favorita encontrada»

#### Scenario: In-flight success wins over abort

- **WHEN** a list request is in flight
- **AND** the operator activates «Tentar de novo» or the previous request is aborted
- **AND** a list payload arrived or will arrive successfully
- **THEN** the screen ends on the list
- **AND** MUST NOT remain on the load error

#### Scenario: Retry with intact catalog ends on the list

- **WHEN** the session is valid
- **AND** the catalog is intact
- **AND** the operator activates «Tentar de novo»
- **THEN** the grade lists the crypto pairs
- **AND** MUST NOT remain on a stuck load error

#### Scenario: Real network failure still uses the #970 error

- **WHEN** the list request fails by real network error or invalid body
- **AND** the session is not dead
- **THEN** the operator sees «Não foi possível carregar as estratégias favoritas.»
- **AND** sees «Tentar de novo»
- **AND** remains on `/favorites`
- **AND** MUST NOT see «Nenhuma estratégia favorita encontrada»

#### Scenario: Dead session goes to login

- **WHEN** the session is truly dead (refresh exhausted, no recoverable access)
- **THEN** the operator is sent to login
- **AND** MUST NOT remain on the Favorites load-error grade pretending the session is valid

#### Scenario: Analysis still has candles and trades

- **WHEN** the operator opens the chart or analysis of a favorite after this change
- **THEN** candles and trades remain available

