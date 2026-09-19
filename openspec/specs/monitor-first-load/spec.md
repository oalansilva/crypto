# monitor-first-load Specification

## Purpose
TBD - created by archiving change card-975-monitor-vazio-favoritos. Update Purpose after archive.
## Requirements
### Requirement: First Monitor visit with crypto favorites shows signals or load error

The first visit to `/monitor` in a valid session that already has crypto favorites (symbol containing `/`) SHALL show analyzed signals on the board **or** the existing load-error copy. The operator MUST NOT need a second click (Atualizar / Tentar de novo / reload workaround) only to leave a false empty catalog. Reloading the same session with the same favorites MUST NOT leave the board stuck on a false empty catalog.

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
- **AND** the analysis fails (network, session, invalid body) **or** returns no rows
- **THEN** the operator sees the existing load error «Não foi possível carregar as estratégias.» with «A lista de favoritos não chegou. Isto não significa que não há estratégias.»
- **AND** sees an action «Tentar de novo»
- **AND** remains on `/monitor`
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: Reload does not stick on false empty

- **WHEN** the same session still has the same crypto favorites
- **AND** the operator reloads `/monitor`
- **THEN** the board shows signals or the existing load error
- **AND** MUST NOT stay on «Nenhum ativo disponível no monitor» as a false empty catalog

### Requirement: Analyzed subset is enough; skipped favorites stay off the board

When analysis returns a subset of the session's crypto favorites, `/monitor` SHALL show the analyzed rows. This change SHALL NOT require every favorite to appear and SHALL NOT add an operator surface for favorites left out of analysis. If every crypto favorite is skipped and the payload is empty, that case SHALL use the load-error copy, not the catalog-empty copy.

#### Scenario: Partial analysis shows the rows that arrived

- **WHEN** the session has more crypto favorites than analyzed opportunities (example from the incident: 18 favorites, 11 analyzed)
- **AND** the analysis payload contains those analyzed rows
- **THEN** the board shows the analyzed signals
- **AND** MUST NOT show «Nenhum ativo disponível no monitor»
- **AND** MUST NOT introduce a «7 de fora» / missing-favorites product state

#### Scenario: Skip-all with favorites is load error

- **WHEN** the session has crypto favorites
- **AND** analysis skips every favorite and returns no rows
- **THEN** the operator sees the existing load error
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

### Requirement: Filter-empty is not catalog-empty

When analysis has arrived with at least one row and a filter hides every signal, `/monitor` SHALL say «Não há resultado com estes filtros.» The default Na carteira vs Todos filter MUST NOT change. Chart / analysis of a visible signal SHALL keep candles and trades.

#### Scenario: A filter hides every loaded signal

- **WHEN** opportunities have loaded
- **AND** a filter (Na carteira, search, stars, strategy, timeframe) hides all of them
- **THEN** the screen says «Não há resultado com estes filtros.»
- **AND** MUST NOT use «Nenhum ativo disponível no monitor»

#### Scenario: Chart still has candles and trades

- **WHEN** the operator opens the chart or analysis of a Monitor signal after this change
- **THEN** candles and trades remain available
- **AND** this card SHALL NOT remove analysis; it SHALL remove the false empty catalog

