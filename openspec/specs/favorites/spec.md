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
The Favorites page MUST be directly accessible to any authenticated user while preserving protected strategy redaction for non-admin users, and its list layout MUST fit common desktop and mobile viewports without horizontal scrolling as the normal workflow.

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

#### Scenario: Desktop favorites list avoids horizontal scrolling
- **WHEN** an authenticated user opens `/favorites` on a common desktop viewport
- **THEN** the Favorites list MUST fit within the viewport without requiring horizontal page or table scrolling
- **AND** tier, symbol, strategy, timeframe, sharpe, trades, return, and analysis actions MUST remain visible
- **AND** direction MAY remain available through the filter without occupying a grid column in the MVP

#### Scenario: Mobile favorites list avoids horizontal scrolling
- **WHEN** an authenticated user opens `/favorites` on a mobile viewport
- **THEN** the Favorites list MUST use the card layout
- **AND** the page MUST fit within the viewport without horizontal scrolling

#### Scenario: Advanced metrics remain accessible
- **WHEN** the desktop viewport cannot fit all advanced metric columns
- **THEN** the grid MAY hide lower-priority advanced metric columns
- **AND** those metrics MUST remain accessible through the existing wide-screen table, export, or analysis flows

### Requirement: Favorites Strategy Visibility
Favorites SHALL expose the Strategy field clearly in the desktop grid and mobile card without exposing protected technical parameters to common users.

#### Scenario: Strategy field visible
- **WHEN** Favorites loads saved strategies
- **THEN** the grid/card SHALL show the strategy label under an explicit Strategy/Estratégia section
- **AND** SHALL preserve existing protected-strategy redaction for common users.

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
The Favorites page SHALL recover missing trade history through the unified favorite analysis action instead of treating a missing `metrics.trades` array as no trades when summary metrics indicate trades exist.

#### Scenario: User opens analysis for favorite without saved trades
- **WHEN** an admin user opens the unified analysis action for a favorite with `total_trades` greater than zero and no saved `metrics.trades`
- **THEN** the UI SHALL request regenerated trades from the Favorites API
- **AND** the result view SHALL render the returned trades
- **AND** the Favorites API SHALL persist the regenerated trades on the favorite so a later open can use saved history

#### Scenario: Regenerated trades have metric mismatch
- **WHEN** the Favorites API reports `metrics_match=false`
- **THEN** the Favorites API SHALL accept the regenerated metrics as the new saved summary for that favorite
- **AND** the Favorites API SHALL persist the previous summary and metric deltas as investigation metadata
- **AND** the UI SHALL open the result view without showing any reconstructed-history mismatch warning to the user
- **AND** the same favorite SHALL NOT regenerate on every open

#### Scenario: Protected favorite remains redacted
- **WHEN** a protected favorite is shown to a non-admin user
- **THEN** the UI SHALL NOT request regenerated protected trades

### Requirement: Favorites uses one analysis action for results and trades
The Favorites page SHALL expose a single analysis action per favorite for users allowed to inspect strategy details, and that flow SHALL show consolidated results and the trade list together.

#### Scenario: Admin reviews a favorite
- **WHEN** an admin user opens the Favorites page
- **THEN** each visible favorite SHALL expose one primary analysis action
- **AND** the row SHALL NOT expose separate `View Trades` and `View Results` actions

#### Scenario: Admin opens combined analysis
- **WHEN** an admin user activates the favorite analysis action
- **THEN** the system SHALL navigate to the result view for that favorite
- **AND** the result view SHALL include consolidated metrics
- **AND** the result view SHALL include the list of trades
- **AND** the result view SHALL provide a visible action to return to Favorites

#### Scenario: Admin reopens saved combined analysis
- **WHEN** an admin user activates the favorite analysis action for a favorite that already has `metrics.trades` and saved chart context
- **THEN** the UI SHALL open the result view using the saved favorite history
- **AND** the UI SHALL NOT request a new combo backtest
- **AND** the UI SHALL NOT regenerate favorite trades

#### Scenario: Admin opens legacy saved trades without chart context
- **WHEN** an admin user activates the favorite analysis action for a favorite with `metrics.trades` but without saved chart context
- **THEN** the UI SHALL request the Favorites API to backfill the analysis cache
- **AND** the result view SHALL include candles for the chart when regeneration returns candles
- **AND** the Favorites API SHALL persist the backfilled chart context so later opens use saved history

#### Scenario: Admin reads combined analysis trades
- **WHEN** the result view renders the favorite trade list
- **THEN** trade table headers and cells SHALL use readable contrast aligned to `DESIGN.md`
- **AND** labels such as `Type`, `Date and time`, and `Signal` SHALL remain legible

#### Scenario: Protected favorite remains protected
- **WHEN** a protected favorite is rendered
- **THEN** the unified analysis action SHALL NOT expose protected strategy parameters or trade regeneration to unauthorized users

### Requirement: Favorites analysis uses Monitor-aligned chart
The Favorites analysis result view SHALL use the same operational chart presentation pattern as the Monitor when candle history is available.

#### Scenario: Favorite analysis opens with candles
- **WHEN** an admin user clicks `Ver análise completa` for a favorite whose analysis has candle history
- **THEN** the result view SHALL render a Monitor-aligned candlestick chart
- **AND** the chart SHALL show readable candles, volume, trade markers, and moving average overlays
- **AND** the chart SHALL expose explicit zoom controls

#### Scenario: Favorite analysis opens without candles
- **WHEN** an admin user opens favorite analysis and no candles are available
- **THEN** the result view SHALL keep an empty chart state
- **AND** the rest of the analysis summary and trades SHALL remain accessible

#### Scenario: Common user opens protected favorite analysis
- **WHEN** a common user opens analysis for a protected favorite with candle history
- **THEN** the result view SHALL render the chart/map
- **AND** the chart SHALL NOT draw moving average overlays
- **AND** the result view SHALL NOT show moving average values or protected strategy parameters

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL use the current market candles source as the primary chart candle source when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. Saved `metrics.analysis_candles` SHALL be used only as a fallback when current market candles cannot be loaded.

#### Scenario: Stale saved candles are replaced by current market candles
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives candles from `/api/market/candles`
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Current candle request fails
- **WHEN** current market candles cannot be loaded for the favorite
- **AND** saved `metrics.analysis_candles` exist
- **THEN** Favorites analysis can still render the saved candles as fallback
- **AND** the failure does not trigger favorite metric regeneration by itself

#### Scenario: Protected common user opens favorite analysis
- **WHEN** a common user opens a protected favorite analysis
- **THEN** the result chart uses current market candles when available
- **AND** the view does not show moving average overlays, moving average values, indicators, or protected parameters

### Requirement: Favorites analysis synchronizes entry and exit signals with Monitor
The Favorites analysis flow SHALL refresh current Monitor opportunity data before rendering entry/exit markers and visible trades. When a matching Monitor opportunity includes signal history, the result chart and trade list SHALL include non-duplicate Monitor-derived entry and exit points without replacing a longer saved or regenerated favorite history.

#### Scenario: Saved trades diverge from Monitor signal history
- **WHEN** a favorite has saved trades with old entry/exit timestamps
- **AND** the matching Monitor opportunity has current `signal_history`
- **AND** the user opens full analysis from Favorites
- **THEN** the visible result chart includes markers derived from Monitor `signal_history`
- **AND** the visible trade list includes non-duplicate entries/exits derived from Monitor `signal_history`
- **AND** saved or regenerated favorite trades remain visible when Monitor history is shorter

#### Scenario: Monitor signal sync unavailable
- **WHEN** Monitor opportunities cannot be loaded or no matching signal history exists
- **AND** the user opens full analysis from Favorites
- **THEN** Favorites falls back to saved/reconstructed trades
- **AND** the failure does not block opening analysis when fallback data exists

#### Scenario: Protected common user opens synced favorite analysis
- **WHEN** a common user opens analysis for a protected favorite
- **AND** Monitor provides redacted signal history
- **THEN** the chart can show safe entry/exit markers from that history
- **AND** protected parameters, indicators, moving averages, and moving-average values remain hidden

### Requirement: Favorites analysis preserves all recoverable trades
The Favorites page SHALL preserve all saved or regenerated trades when opening a full analysis result from a favorite, even when Monitor synchronization returns a shorter `signal_history`.

#### Scenario: Monitor sync has fewer trades than favorite history
- **WHEN** the user opens full analysis from a favorite with saved or regenerated trades
- **AND** Monitor synchronization returns fewer trades for the same strategy
- **THEN** the result trade list SHALL include the saved or regenerated favorite trades
- **AND** the Monitor synchronization SHALL NOT replace the favorite trade list with the shorter Monitor set

#### Scenario: Monitor sync adds a missing current trade
- **WHEN** the user opens full analysis from a favorite
- **AND** Monitor synchronization returns a trade not already present in the saved or regenerated favorite history
- **THEN** the result trade list SHALL include that additional Monitor trade
- **AND** duplicate trades from both sources SHALL appear only once

#### Scenario: Protected favorite remains redacted for common user
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the result SHALL preserve the protected favorite's available trades
- **AND** the result SHALL NOT expose protected parameters, indicators, moving-average overlays, or moving-average values

### Requirement: Favorites does not expose agent chat action
The Favorites page SHALL NOT expose a "Chat com agente", "Trader", or equivalent agent-chat action from `/favorites`, while preserving the existing Favorites analysis, ranking, filtering, selection, and administrative delete actions.

#### Scenario: Desktop Favorites row hides agent chat
- **WHEN** an admin user opens `/favorites` on a desktop viewport
- **THEN** each visible favorite SHALL keep the analysis action
- **AND** administrative users SHALL keep the delete action
- **AND** the row actions SHALL NOT include "Chat com agente", "Trader", or a chat icon action that opens the agent chat modal

#### Scenario: Mobile Favorites card hides agent chat
- **WHEN** an admin user opens `/favorites` on a mobile viewport
- **THEN** each visible favorite card SHALL keep the analysis action
- **AND** administrative users SHALL keep the delete action
- **AND** the card actions SHALL NOT include "Chat com agente", "Trader", or a chat icon action that opens the agent chat modal

### Requirement: Favorites expose automatic backtest refresh state
The Favorites API and UI SHALL expose the last automatic refresh state for each favorite strategy.

#### Scenario: User lists favorites after an automatic refresh
- **WHEN** a user opens Favorites
- **THEN** each favorite response SHALL include refresh status, refresh run id, start timestamp, completion timestamp, and error when available
- **AND** the Favorites UI SHALL show a compact last update/status line for each favorite

#### Scenario: Protected favorite is listed
- **WHEN** a protected favorite is listed for a common user
- **THEN** refresh metadata MAY be shown
- **AND** protected strategy parameters and implementation details SHALL remain redacted

### Requirement: Favorites remains chart data base
Favorites result charts SHALL remain driven by the complete result payload available on `/combo/results`.

#### Scenario: Saved result chart opens without extra candle fetch
- **WHEN** a saved favorite result includes candle and marker history
- **THEN** the chart SHALL render from the saved result payload
- **AND** it SHALL NOT require Monitor-specific opportunity data to display the full chart.

### Requirement: Common users can inspect safe catalog favorites
The favorites API SHALL allow a common user to read favorite details from the admin catalog when that favorite is part of the safe catalog path.

#### Scenario: Common user opens admin catalog favorite detail
- **WHEN** the requested favorite belongs to the admin catalog
- **THEN** the API returns the favorite detail without exposing another common user's private favorite data

#### Scenario: Common user opens private favorite from another user
- **WHEN** the requested favorite is not owned by the current user and is not an admin catalog favorite
- **THEN** the API returns not found

