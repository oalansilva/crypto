# favorites Specification

## Purpose
TBD - created by syncing delta from change save-combo-favorites. Save combo strategy from results to favorites.
## Requirements
### Requirement: Salvar Estratégia dos Resultados do Combo
O sistema SHALL fornecer um mecanismo para salvar uma configuração específica de estratégia (incluindo parâmetros e métricas) da página de Resultados do Backtest de Combo para a lista de Favoritos. O fluxo inclui um botão "Salvar nos Favoritos" e um modal para nome e notas; o sistema SHALL evitar duplicatas, apresentando aviso para sobrescrever ou salvar como novo.

#### Scenario: Salvar nova estratégia
- **WHEN** the user clicks "Salvar nos Favoritos" on a new combo result
- **THEN** the system SHALL open a modal with name and optional notes
- **AND** the strategy SHALL be persisted to the favorites list

#### Scenario: Duplicate name warning
- **WHEN** the user enters a name that already exists in favorites
- **THEN** the system SHALL display a warning offering to overwrite or save as a new entry

### Requirement: Campo de Notas
O modal de salvamento SHALL incluir campo opcional "Notas", que SHALL ser persistido no banco junto com a estratégia.

#### Scenario: Notas persistidas
- **WHEN** the user fills in the optional notes field and saves
- **THEN** the notes SHALL be stored alongside the strategy in the database
- **AND** the notes SHALL be displayed when viewing the favorite

### Requirement: Armazenar Métricas Compostas
O sistema SHALL armazenar `total_return` como Retorno Composto ao salvar nos Favoritos. O painel de Favoritos SHALL exibir o mesmo retorno composto, não soma simples.

#### Scenario: Compound return stored and displayed
- **WHEN** the user saves a combo strategy to favorites
- **THEN** the system SHALL store `total_return` as the compound return
- **AND** the Favorites panel SHALL display the compound return, not a simple sum

### Requirement: Favorites hide strategy secrets from non-admin users
The Favorites API and UI MUST hide clear strategy implementation details from non-admin users.

#### Scenario: Non-admin lists favorites
- **WHEN** a non-admin user lists saved favorite strategies
- **THEN** each favorite MUST avoid exposing the original strategy name
- **AND** each favorite MUST avoid exposing saved strategy parameter values
- **AND** each favorite MUST mark the strategy as protected

#### Scenario: Admin lists favorites
- **WHEN** an admin user lists saved favorite strategies
- **THEN** each favorite MUST include the original strategy name and parameter values as before
- **AND** each favorite MUST mark the strategy as not protected

### Requirement: Favorites screen is available to authenticated users
The Favorites page MUST be directly accessible to any authenticated user while preserving protected strategy redaction for non-admin users.

#### Scenario: Non-admin opens favorites route
- **WHEN** a non-admin user opens `/favorites`
- **THEN** the frontend MUST render the Favorites page
- **AND** the page MUST list the admin-generated favorite strategy catalog
- **AND** the page MUST avoid exposing original strategy names, parameter values, or admin-only strategy actions for protected favorites
- **AND** the page MUST provide a star control to choose monitoring priority

#### Scenario: Admin opens favorites route
- **WHEN** an admin user opens `/favorites`
- **THEN** the frontend MUST render the existing favorites workflow
- **AND** the admin user MAY still see strategy internals and admin actions allowed by existing permissions

### Requirement: Favorites tier selection uses stars
The Favorites page MUST allow users to set the existing favorite tier through a star-based control.

#### Scenario: User marks three stars
- **WHEN** the user chooses three stars for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=1`
- **AND** the backend MUST persist that tier as the current user's preference when the favorite belongs to an admin

#### Scenario: User marks two stars
- **WHEN** the user chooses two stars for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=2`
- **AND** the backend MUST persist that tier as the current user's preference when the favorite belongs to an admin

#### Scenario: User marks one star
- **WHEN** the user chooses one star for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=3`
- **AND** the backend MUST persist that tier as the current user's preference when the favorite belongs to an admin

#### Scenario: User clears stars
- **WHEN** the user clears the star selection for a favorite
- **THEN** the frontend MUST PATCH that favorite with `tier=null`
- **AND** the backend MUST clear that tier for the current user's preference when the favorite belongs to an admin

### Requirement: Favorites Strategy filter uses only strategy labels
The Favorites page Strategy filter MUST list and match only strategy labels, not symbols, timeframes, hours, or free-form favorite names.

#### Scenario: Favorites page builds Strategy options
- **WHEN** the Favorites page loads crypto favorites
- **THEN** the Strategy filter options MUST be derived from the favorite strategy label
- **AND** Strategy options MUST NOT include symbol text such as `BTC/USDT` or `ETH/USDT`
- **AND** Strategy options MUST NOT include timeframe text such as `1h` or `4h`
- **AND** timeframe values MUST remain available only in the Time filter

#### Scenario: User filters by strategy label
- **WHEN** the user selects a Strategy option
- **THEN** the page MUST show favorites whose strategy label matches that option
- **AND** the filter MUST not depend on the favorite nickname

### Requirement: Favorites owns strategy curation for Monitor
The Favorites screen SHALL be the canonical UI for choosing, removing, and ranking strategies that feed the Monitor. The Monitor SHALL consume Favorites ranking as read-only tier/star classification and SHALL NOT duplicate favorite curation controls.

#### Scenario: User changes strategy ranking
- **WHEN** the user wants to change a strategy star/tier ranking
- **THEN** the user MUST do that on the Favorites screen
- **AND** the Monitor reflects that ranking as read-only classification

#### Scenario: User removes a strategy from curation
- **WHEN** the user wants to remove a strategy from the monitored favorite catalog
- **THEN** the user MUST do that on the Favorites screen
- **AND** the Monitor MUST NOT expose a separate remove-favorite action

### Requirement: Favorites View Trades recovers missing history
The Favorites page SHALL recover missing trade history for visible admin favorites instead of treating a missing `metrics.trades` array as no trades when summary metrics indicate trades exist.

#### Scenario: User clicks View Trades for favorite without saved trades
- **WHEN** an admin user clicks `View Trades` for a favorite with `total_trades` greater than zero and no saved `metrics.trades`
- **THEN** the UI SHALL request regenerated trades from the Favorites API
- **AND** the trade modal SHALL render the returned trades

#### Scenario: Regenerated trades have metric mismatch
- **WHEN** the Favorites API reports `metrics_match=false`
- **THEN** the UI SHALL open the trades modal with a non-blocking warning that regenerated trades do not fully match the saved summary metrics

#### Scenario: Protected favorite remains redacted
- **WHEN** a protected favorite is shown to a non-admin user
- **THEN** the UI SHALL NOT request regenerated protected trades

