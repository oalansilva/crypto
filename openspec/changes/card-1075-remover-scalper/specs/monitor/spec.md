## ADDED Requirements

### Requirement: Authenticated Monitor has no scalper module
Authenticated `/monitor` SHALL NOT render the Scalp BTCUSDT module, switch, diagnosis, kill banner, or any other scalper element. The rest of the workbench SHALL remain: Em posição, Saída / cobertura, KPIs, filters, `table.signals`, and Operar. The page SHALL NOT announce that a scalper was removed. This card SHALL NOT add a catalog route and SHALL NOT restyle opportunity cards, signal states, or the Operar confirmation modal.

#### Scenario: Monitor without the scalper
- **WHEN** an authenticated user opens `/monitor` on desktop or mobile
- **THEN** no scalper or scalp element SHALL be visible
- **AND** Em posição, Saída / cobertura, KPIs and filters SHALL still work as they do today
- **AND** `table.signals` SHALL still expose Status, Preço, Distância, 7d, Risco até stop, Tags, Operar and Par / Estratégia
- **AND** the Operar control SHALL still open the existing confirmed MARKET flow
- **AND** the page SHALL NOT contain a banner or copy that the scalper left

## REMOVED Requirements

### Requirement: Monitor hosts the directional scalp module without redesigning Operar
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). The module no longer sits on `/monitor`.
**Migration**: Keep the existing board and Operar. Do not replace the module with a discontinuation notice.

#### Scenario: Former scalp module is gone
- **WHEN** an authenticated user opens `/monitor`
- **THEN** the Scalp BTCUSDT module SHALL NOT be present
- **AND** Operar SHALL remain on the board

### Requirement: Monitor scalp module gains a rolling 15 min lookback without redesigning the board or Operar
**Reason**: The scalper module is removed, so lookback, hurdle, target, stop and «posição presa» no longer belong on `/monitor`.
**Migration**: Board columns and Operar stay. No new route.

#### Scenario: Lookback facts leave with the module
- **WHEN** an authenticated user opens `/monitor`
- **THEN** the page SHALL NOT show scalp lookback, hurdle, target, stop or «posição presa»
- **AND** `table.signals` and Operar SHALL remain

### Requirement: Scalp panel shows livro indisponível when the book is not fresh
**Reason**: The scalper panel is removed, so «livro indisponível» on that panel no longer applies.
**Migration**: The shared `@ticker` stream used by the rest of the Farol is unchanged. Operar is unchanged.

#### Scenario: No scalp status line
- **WHEN** an authenticated user opens `/monitor`
- **THEN** there SHALL be no scalp status line
- **AND** the board SHALL remain
