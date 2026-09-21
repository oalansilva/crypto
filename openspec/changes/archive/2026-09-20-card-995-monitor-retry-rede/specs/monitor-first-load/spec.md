## MODIFIED Requirements

### Requirement: First Monitor visit with crypto favorites shows signals or load error

The first visit to `/monitor` in a valid session that already has crypto favorites (symbol containing `/`) SHALL show analyzed signals on the board **or** the existing load-error copy. A transient network cut MUST be reabsorbed during that visit: the operator waits tens of seconds in «Carregando sinais...» and MUST NOT need a second click only because the first authenticated request was cut. The operator MUST NOT need a second click (Atualizar / Tentar de novo / reload workaround) only to leave a false empty catalog. Reloading the same session with the same favorites MUST NOT leave the board stuck on a false empty catalog.

#### Scenario: First visit lists analyzed signals

- **WHEN** the session is valid
- **AND** crypto favorites are visible in `/favorites`
- **AND** the operator opens `/monitor` for the first time in that session
- **AND** the analysis returns at least one opportunity
- **THEN** the board shows those signals on the first paint
- **AND** the operator MUST NOT see «Nenhum ativo disponível no monitor»
- **AND** the operator MUST NOT be required to click Atualizar only to make the board stop being empty

#### Scenario: First visit analysis fails or returns no rows while favorites exist

- **WHEN** the session is valid
- **AND** crypto favorites are visible in `/favorites`
- **AND** the operator opens `/monitor`
- **AND** the analysis fails persistently (invalid body, skip-all, or network still failing after the wait) **or** returns no rows
- **THEN** the operator sees the existing load error «Não foi possível carregar as estratégias.» with «A lista de favoritos não chegou. Isto não significa que não há estratégias.»
- **AND** sees an action «Tentar de novo»
- **AND** remains on `/monitor`
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: First visit absorbs a transient network cut

- **WHEN** the session is valid
- **AND** crypto favorites are on the server
- **AND** the operator opens `/monitor`
- **AND** the first authenticated list request is cut
- **THEN** the board shows «Carregando sinais...» for tens of seconds
- **AND** MUST NOT paint the #975 error on that first cut
- **AND** if the list arrives in the same opening, the board lists the pairs without a second click

#### Scenario: Reload does not stick on false empty

- **WHEN** the same session still has the same crypto favorites
- **AND** the operator reloads `/monitor`
- **THEN** the board shows signals or the existing load error
- **AND** MUST NOT stay on «Nenhum ativo disponível no monitor» as a false empty catalog
