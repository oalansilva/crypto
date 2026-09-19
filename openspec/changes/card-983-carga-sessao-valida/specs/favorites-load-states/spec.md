## ADDED Requirements

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
