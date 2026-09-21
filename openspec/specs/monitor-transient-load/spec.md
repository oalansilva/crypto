# monitor-transient-load Specification

## Purpose
TBD - created by archiving change card-995-monitor-retry-rede. Update Purpose after archive.
## Requirements
### Requirement: Transient network cut is absorbed before the #975 error

On `/monitor`, with a valid session and crypto favorites on the server, a transient network cut of the authenticated list request MUST NOT be the last word on the first failure. The app SHALL keep the operator in the loading state for tens of seconds (the length of an opening stuck on the corporate proxy) and SHALL reabsorb a later success in the same opening. Only after that wait, if the list still did not arrive, SHALL the existing #975 load-error copy appear. This change SHALL NOT alter Caddy, payload size, backend `GET /api/opportunities/` (already 200), Zscaler, session TTL, or the board layout.

#### Scenario: Incident opening lists the pairs without changing network

- **WHEN** the administrator opens `/monitor` with a valid session
- **AND** 11 strategies are on the server
- **AND** the first authenticated list request is cut (browser does not receive the JSON)
- **THEN** the board lists the pairs after the app reabsorbs the cut
- **AND** the operator MUST NOT have to change network
- **AND** MUST NOT see «Não foi possível carregar as estratégias.» as the first paint of that opening
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: Wait tens of seconds in loading before #975

- **WHEN** the authenticated list request is cut and the session is still valid
- **AND** the list has not arrived yet
- **THEN** the board shows «Carregando sinais...»
- **AND** MUST NOT paint the #975 error on that first cut
- **AND** if the proxy stays stuck for minutes, the operator uses «Tentar de novo»

#### Scenario: Successful load in the same opening hides error and preferences toast

- **WHEN** the session is valid
- **AND** the list eventually arrives in the same opening
- **THEN** `table.signals` lists the pairs
- **AND** MUST NOT leave the list-error card visible
- **AND** MUST NOT leave «Não foi possível carregar preferências do monitor.» visible

### Requirement: KPIs are not a true zero while the list is still loading

While `/monitor` is waiting for the list, KPI values SHALL NOT appear as a completed count of zero (as if there were no signals). Labels of the KPI strip stay as they are (no redesign). When the list arrives, KPI values reflect the loaded signals.

#### Scenario: Loading does not paint KPI 0 as truth

- **WHEN** the operator is in «Carregando sinais...»
- **THEN** the KPI numeric values MUST NOT show `0` as a completed count
- **AND** the board still shows «Carregando sinais...»

### Requirement: Retry rereads; Atualizar still recomputes

After a load error, «Tentar de novo» SHALL request the already-computed list again and MUST NOT recompute. «Atualizar» SHALL keep recomputing.

#### Scenario: Tentar de novo rereads the computed list

- **WHEN** the operator is on the #975 load-error card
- **AND** the operator activates «Tentar de novo»
- **THEN** the app asks again for the list already calculated
- **AND** MUST NOT send a recompute (`refresh=true`) for that action

#### Scenario: Atualizar still recomputes

- **WHEN** the operator activates «Atualizar»
- **THEN** the app still recomputes the analysis

### Requirement: Dead session goes to login; persistent failure keeps #975

If the session is truly dead, `/monitor` SHALL send the operator to login and MUST NOT keep them on the load-error card. A real persistent failure SHALL keep the #975 copy («Não foi possível carregar as estratégias.» + «A lista de favoritos não chegou…» + «Tentar de novo») and MUST NOT fake an empty catalog. Favorites, Home, and Wallet stay on the #983 contract.

#### Scenario: Dead session goes to login

- **WHEN** the session is truly dead (refresh exhausted, no recoverable access)
- **AND** the operator is on `/monitor`
- **THEN** the operator reaches login
- **AND** MUST NOT remain on the Monitor load-error card

#### Scenario: Persistent failure keeps the #975 copy

- **WHEN** the list still did not arrive after the wait
- **AND** the session is not dead
- **THEN** the operator sees «Não foi possível carregar as estratégias.»
- **AND** sees «A lista de favoritos não chegou. Isto não significa que não há estratégias.»
- **AND** sees «Tentar de novo»
- **AND** remains on `/monitor`
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

