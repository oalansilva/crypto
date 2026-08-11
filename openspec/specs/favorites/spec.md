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
O sistema SHALL armazenar `total_return` como Retorno Composto ao salvar nos Favoritos. O painel de Favoritos SHALL exibir o mesmo retorno composto, não soma simples. O sistema MUST preserve `total_return_pct` and `total_pnl_pct` as percentage-point values from the backend and MUST NOT multiply those fields by 100 again when persisting or rendering Favorites metrics.

#### Scenario: Compound return stored and displayed
- **WHEN** the user saves a combo strategy to favorites
- **THEN** the system SHALL store `total_return` as the compound return
- **AND** the Favorites panel SHALL display the compound return, not a simple sum

#### Scenario: Backend percentage is not multiplied twice
- **WHEN** a favorite metric payload contains `total_return_pct=42`
- **THEN** the Favorites page MUST render the return as `+42.00%`
- **AND** the save flow MUST NOT persist the same value as `4200`

#### Scenario: Ratio metrics still render as percentages
- **WHEN** a favorite metric payload contains ratio fields such as `win_rate=0.6`, `max_drawdown=0.11`, or `total_return=0.42`
- **THEN** the Favorites page MUST render those values as `60.00%`, `11.00%`, and `+42.00%` respectively

### Requirement: Favorites hide strategy secrets from non-admin users
The Favorites API and UI MUST hide implementation-only strategy secrets from non-admin users while exposing the canonical functional transparency manifest.

#### Scenario: Non-admin lists favorites
- **WHEN** a non-admin user lists saved favorite strategies
- **THEN** each favorite MUST include its specific public name, description and public manifest summary
- **AND** MUST omit source code, credentials, raw diagnostics and unauthorized mutation controls
- **AND** MUST NOT replace the public identity with a generic protected label.

#### Scenario: Admin lists favorites
- **WHEN** an admin user lists saved favorite strategies
- **THEN** each favorite MUST include the same public manifest
- **AND** MAY additionally include original identifiers and technical fields authorized for audit.

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
The Favorites page Strategy filter MUST list and match only strategy labels, not symbols, timeframes, hours, or free-form favorite names. For protected favorites shown to common users, the system MUST provide a distinct safe strategy display label for filtering while keeping raw strategy implementation details redacted.

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

#### Scenario: Common user filters protected favorites by safe strategy label
- **WHEN** a common user opens Favorites with multiple protected strategies
- **THEN** the Strategy filter MUST include distinct safe strategy labels instead of only the generic protected label
- **AND** selecting a safe strategy label MUST filter the list to favorites with that label
- **AND** the page MUST keep raw strategy names, parameters, and indicators hidden

#### Scenario: Common user opens protected favorite chart
- **WHEN** a common user opens the chart or full analysis for a protected favorite
- **THEN** the chart title MUST show the same safe strategy label used by the Favorites filter
- **AND** the chart MUST NOT show raw strategy names, parameters, or protected indicator values

#### Scenario: Favorite chart opens when monitor sync is slow
- **WHEN** a user opens full analysis for a favorite that already has saved chart context
- **AND** monitor opportunity refresh or trade sync is slow
- **THEN** the system MUST open the favorite chart using saved or current candle data without waiting indefinitely for monitor sync
- **AND** monitor sync MAY be skipped for that open

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
The Favorites analysis result view SHALL use the shared Monitor-aligned chart and the canonical public indicator contract when candle history is available.

#### Scenario: Favorite analysis opens with candles and indicators
- **WHEN** a user opens full analysis for a favorite with candle and timestamped indicator history
- **THEN** the result SHALL show readable candles, volume, complete trade markers and manifest-defined indicator panels
- **AND** SHALL preserve explicit zoom and the `Analisar` flow.

#### Scenario: Favorite analysis opens without candles
- **WHEN** a user opens favorite analysis and no candles are available
- **THEN** the result SHALL keep an explicit empty chart state
- **AND** the manifesto, summary and trades SHALL remain accessible.

#### Scenario: Common user opens protected favorite analysis
- **WHEN** a common user opens analysis for a protected favorite
- **THEN** the result SHALL show public indicators, parameters and functional explanations from the canonical manifest
- **AND** SHALL keep implementation-only fields and unauthorized regeneration hidden.

### Requirement: Favorites analysis uses current market candles for chart rendering
The Favorites analysis flow SHALL merge available candle sources when opening a favorite analysis. Saved favorite trades and metrics SHALL remain the source for summary and trade evidence. The `/api/market/candles?full_history=true` data for the favorite symbol/timeframe SHALL be requested so the chart can use all persisted historical candles for the asset, independent of strategy. Saved `metrics.analysis_candles` SHALL be merged with market candles by timestamp so older backtest history and recent market candles both remain visible.

#### Scenario: Stale saved candles are replaced by full market history
- **WHEN** a favorite has saved `metrics.analysis_candles` ending before the current market candle window
- **AND** the full market candle series has at least as many candles as the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart receives the merged saved and market candle series
- **AND** the newest chart candle matches the newest candle returned by `/api/market/candles`
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Saved full-history candles are longer than market history response but older
- **WHEN** a favorite has saved `metrics.analysis_candles` covering a longer backtest history than the market candle response
- **AND** `/api/market/candles?full_history=true` returns newer candles after the saved chart context
- **AND** the user opens full analysis from Favorites
- **THEN** the result chart includes the saved older candles and the newer market candles
- **AND** saved trades and metrics remain available in the result view

#### Scenario: Current candle request fails
- **WHEN** current market candles cannot be loaded for the favorite
- **AND** saved `metrics.analysis_candles` exist
- **THEN** Favorites analysis can still render the saved candles as fallback
- **AND** the failure does not trigger favorite metric regeneration by itself

#### Scenario: Full persisted market history is incomplete
- **WHEN** Favorites analysis requests `/api/market/candles?full_history=true`
- **AND** the persisted OHLCV table does not cover the configured historical window or is stale
- **THEN** the backend schedules an OHLCV backfill job for the favorite symbol/timeframe
- **AND** the current request still returns the best available candle series
- **AND** future requests can use the backfilled candles after the job writes them

#### Scenario: Backend starts with favorite symbols already registered
- **WHEN** the OHLCV backfill scheduler starts
- **THEN** it includes crypto symbols/timeframes found in Favorites by default
- **AND** it runs an initial scheduler pass without waiting for the daily interval
- **AND** missing historical candles can be fetched in the background before the user opens the chart

#### Scenario: Protected common user opens favorite analysis
- **WHEN** a common user opens a protected favorite analysis
- **THEN** the result chart uses the most complete allowed candle source
- **AND** the view does not show moving average overlays, moving average values, indicators, or protected parameters

### Requirement: New hard-mode Favorite has visible final metrics
When a hard-mode BTC discovery run saves a BTC/USDT 1d long Favorite, the system SHALL expose the new Favorite through `/api/favorites/` with the new id, public name, technical strategy name, updated deep backtest metrics, and no pending backtest placeholder.

#### Scenario: Saved Favorite is read back through Favorites API
- **WHEN** the new Favorite is saved and any required refresh completes
- **THEN** `/api/favorites/` returns the Favorite by id with updated metrics and without "Backtest aguardando atualização"

### Requirement: New hard-mode Favorite exposes trade evidence
When a hard-mode BTC discovery run saves a BTC/USDT 1d long Favorite, the system SHALL expose trade history or equivalent cached trade evidence for the saved Favorite.

#### Scenario: Saved Favorite trades are queryable
- **WHEN** the new Favorite id is requested through `/api/favorites/{id}/trades` or an equivalent endpoint
- **THEN** the response proves the saved Favorite has backtest trade evidence for the final strategy

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

### Requirement: Favorites list ordering follows the selected sort option
The Favorites page MUST apply the selected ordering option as the primary sort key for the visible filtered Favorites list.

#### Scenario: User changes Favorites ordering
- **WHEN** an authenticated user opens `/favorites`
- **AND** selects an available option in the `Ordenar` control
- **THEN** the visible Favorites list MUST reorder according to that selected option
- **AND** the list MUST update immediately without requiring a page reload

#### Scenario: User changes Favorites ordering repeatedly
- **WHEN** the user changes the `Ordenar` control more than once
- **THEN** each selected ordering option MUST be reflected by the visible Favorites list
- **AND** ties MUST be resolved deterministically

#### Scenario: Favorites ordering handles small result sets
- **WHEN** the filtered Favorites list is empty or contains one item
- **THEN** changing the `Ordenar` control MUST NOT break the screen or show a visual error

### Requirement: Favorites analysis preserves all recoverable trades
The Favorites page SHALL preserve all saved or regenerated trades when opening a full analysis result, even when Monitor synchronization returns a shorter `signal_history`.

#### Scenario: Monitor sync has fewer trades than favorite history
- **WHEN** Monitor synchronization returns fewer trades than the saved or regenerated favorite history
- **THEN** the result trade list and chart markers SHALL retain all recoverable favorite trades.

#### Scenario: Monitor sync adds a missing current trade
- **WHEN** Monitor synchronization returns a non-duplicate trade absent from favorite history
- **THEN** the result SHALL include it once in the list and marker source.

#### Scenario: Common user opens protected favorite
- **WHEN** a common user opens full analysis for a protected favorite
- **THEN** the result SHALL preserve trades and canonical public indicators
- **AND** SHALL keep source code, diagnostics and unauthorized mutation controls hidden.

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

### Requirement: Favorites Preserve Strategy Direction

Favorites SHALL preserve strategy direction across save, list, regeneration and trade-analysis flows.

#### Scenario: Short favorite regeneration uses short direction

- **GIVEN** a saved favorite has `parameters.direction == "short"`
- **WHEN** `/api/favorites/{id}/trades` regenerates analysis
- **THEN** regeneration SHALL call the modern combo optimizer with `direction == "short"`
- **AND** returned trades SHALL use short-side profit and stop semantics

#### Scenario: Missing direction remains long compatible

- **GIVEN** an existing favorite does not include direction
- **WHEN** it is listed or regenerated
- **THEN** the system SHALL treat it as `long`

### Requirement: Favorites exposes canonical strategy transparency
Favorites list and analysis responses SHALL expose the same strategy transparency contract used by Monitor.

#### Scenario: Favorite is opened in list and analysis
- **WHEN** a favorite appears in both surfaces
- **THEN** name, description, parameters, indicator metadata and logic explanations SHALL be identical
- **AND** analysis SHALL add timestamped series without redefining the manifest.

#### Scenario: Legacy favorite has aligned cached series but no persisted manifest
- **WHEN** a favorite created before strategy transparency has cached candles and indicator arrays with a proven one-to-one timestamp source
- **AND** its list payload has no usable timestamped transparency series
- **THEN** opening full analysis SHALL request the favorite analysis response that reconstructs the canonical timestamped series
- **AND** `/combo/results` SHALL render the declared overlays or panels
- **AND** the Favorites list SHALL remain a summary payload without duplicating full historical series for every row.

### Requirement: Favorite analysis indicators cover current candles
Opening full favorite analysis SHALL return public indicator series calculated by the backend over the same current OHLCV snapshot returned as chart candles, without rerunning trade optimization.

#### Scenario: Cached analysis is older than canonical candles
- **WHEN** a favorite has saved trades and indicator arrays ending before the current canonical OHLCV history
- **THEN** the analysis response SHALL preserve the saved trades and metrics
- **AND** SHALL recalculate only the declared indicator columns using the favorite's effective parameters
- **AND** every available moving-average series SHALL end at the same timestamp as the last returned candle.

#### Scenario: Current OHLCV reconstruction fails
- **WHEN** current canonical candles cannot be loaded or calculated safely
- **THEN** the analysis SHALL fall back to the proven cached candles and series
- **AND** SHALL NOT align arrays positionally or regenerate trades implicitly.

#### Scenario: Common trader receives current reconstruction
- **WHEN** a non-admin trader is authorized to view the favorite analysis
- **THEN** the response SHALL include current timestamped public series and candles
- **AND** SHALL keep raw `indicator_data`, diagnostics and implementation configuration hidden.

### Requirement: Favorites analysis has one decision-first reading hierarchy
The full analysis opened from Favorites SHALL present information in the order identity and decision summary, permanent strategy rules, chart evidence, technical configuration, and trades. Summary content SHALL prioritize symbol, strategy name, timeframe, direction, return, win rate, drawdown and trade count without repeating the full effective configuration.

#### Scenario: Trader opens a complete favorite analysis
- **WHEN** an authorized trader opens full analysis from Favorites
- **THEN** the first viewport SHALL identify the strategy and expose its primary performance and risk context
- **AND** permanent entry and exit rules SHALL appear before the detailed technical configuration
- **AND** the chart SHALL remain the primary evidence surface.

#### Scenario: Analysis has a long strategy description
- **WHEN** the public strategy description exceeds the available width on desktop or mobile
- **THEN** the analysis SHALL wrap the complete description without clipping or horizontal scrolling
- **AND** SHALL preserve the strategy identity and summary hierarchy.

### Requirement: Favorites analysis uses progressive disclosure for technical detail
The full analysis SHALL keep the technical configuration available through an explicit accessible disclosure while keeping the essential decision context visible by default. Indicator definitions, effective parameters and unavailability explanations SHALL NOT be repeated in multiple page sections.

#### Scenario: Trader needs technical configuration
- **WHEN** the trader activates the technical-details disclosure
- **THEN** the analysis SHALL expose every public indicator and effective parameter available in the canonical manifest
- **AND** each indicator or parameter SHALL appear once within the analysis presentation outside the chart legend's point-in-time values.

#### Scenario: Technical evidence is unavailable
- **WHEN** an indicator series or effective configuration cannot be proven
- **THEN** the analysis SHALL present one explicit unavailable explanation in the relevant technical-detail context
- **AND** SHALL keep the chart, summary, rules and trades usable.

#### Scenario: Indicator series is available
- **WHEN** an indicator series is available for the current timeframe
- **THEN** the analysis SHALL render the series and its evidence without a positive availability message
- **AND** SHALL reserve availability copy for unavailable, absent, or incompatible evidence.

### Requirement: Favorites uses canonical signals without a duplicate history panel
The Favorites analysis SHALL use the canonical Monitor signal history as chart evidence when available and SHALL NOT render a separate signal-history list, loading state, error state, or empty state below the chart.

#### Scenario: Monitor signal history is synchronized
- **WHEN** the Favorites analysis receives canonical Monitor signal history for the same strategy, symbol, direction, and timeframe
- **THEN** those events SHALL be represented as chart markers
- **AND** the page SHALL NOT render `Histórico de sinais`, `Últimos do Monitor`, or a separate list of those events.

#### Scenario: Monitor signal history is temporarily unavailable
- **WHEN** Monitor synchronization times out, fails, or has no matching history
- **THEN** the chart MAY use the existing trade-marker fallback
- **AND** the Favorites page SHALL NOT render a separate synchronization warning for signal history.

### Requirement: Favorites analysis remains usable across responsive layouts
The analysis SHALL preserve its information hierarchy, actions and complete readable content on desktop and mobile without requiring horizontal page scrolling.

#### Scenario: Trader opens analysis on mobile
- **WHEN** the viewport width is below 768 pixels
- **THEN** summary metrics and strategy rules SHALL reflow into a linear, scannable composition
- **AND** chart controls and technical disclosure SHALL remain keyboard and touch accessible
- **AND** labels, descriptions and values SHALL not be clipped.

### Requirement: Favorites result parameter labels are trader-facing
Favorites result charts SHALL render visible strategy parameter labels and common parameter values in trader-facing Portuguese instead of raw internal keys and English values.

#### Scenario: Favorite result shows translated parameters
- **WHEN** a user opens a favorite analysis result with visible parameters including `direction`, `ema_short`, `sma_medium`, `sma_long`, `stop_loss`, and `data_source`
- **THEN** the result configuration SHALL show Portuguese labels such as `Direção`, `EMA curta`, `SMA média`, `SMA longa`, `Stop de perda`, and `Fonte de dados`
- **AND** common values SHALL be shown as trader-facing values such as `Compra` and `CCXT`
- **AND** raw labels such as `direction`, `ema short`, `sma medium`, `sma long`, `stop loss`, and `data source` SHALL NOT appear in that configuration block

#### Scenario: Protected favorite result keeps parameters hidden
- **WHEN** a common user opens a protected favorite result
- **THEN** technical parameters SHALL remain hidden behind the protected-parameters message

### Requirement: Favorites search supports combined terms
Favorites SHALL match free-text searches when all typed terms appear across the combined favorite identity, including symbol, quote, strategy name, displayed strategy label, favorite name, description, and timeframe.

#### Scenario: Search spans symbol and strategy
- **WHEN** a user searches Favorites for `BTC/USDT USDT multi ma crossoverV2`
- **THEN** the BTC/USDT favorite using `multi_ma_crossoverV2` SHALL remain visible when other filters allow it

#### Scenario: Existing single-field search remains supported
- **WHEN** a user searches Favorites for a symbol, strategy word, or favorite name fragment
- **THEN** matching favorites SHALL remain visible

