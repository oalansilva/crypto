# discovery-catalog-selection Specification

## Purpose
TBD - created by archiving change card-469-selection-redesign. Update Purpose after archive.
## Requirements
### Requirement: Compact catalog summaries

The Discovery draft SHALL represent Templates and Symbols as compact selection summaries instead of rendering the catalog as an open vertical list in the form.

#### Scenario: Default draft

- **WHEN** the administrator opens `/combo/discovery` on a new draft
- **THEN** each catalog summary shows the selected count, an explicit edit action, and representative selected items only when at least one item is selected
- **AND** a new draft shows count 0, no chips, and empty selection for Templates and for Symbols
- **AND** timeframe, direction, period, ranking, preflight, active sweep, history, and leaderboard retain their existing hierarchy.

### Requirement: No-scroll catalog workbench

The catalog workbench SHALL fit its selection controls and one bounded result page inside the available desktop and mobile viewport without requiring vertical scrolling to reach an option or the apply/cancel actions.

#### Scenario: Desktop catalog access

- **WHEN** the workbench is opened at 1440 × 900
- **THEN** it shows at most six result options at once
- **AND** search, category, pagination, selection summary, cancel, and apply remain reachable without scrolling the workbench.

#### Scenario: Mobile catalog access

- **WHEN** the workbench is opened at 390 × 844
- **THEN** it shows at most four result options at once
- **AND** the dialog, result area, and actions fit without vertical scrolling.

### Requirement: Every item remains reachable

The workbench SHALL make every one of the 30 templates and 126 symbols reachable through instant search, category filtering, or pagination without materializing a long visible list.

#### Scenario: Reach the final symbol directly

- **WHEN** the administrator searches for `ZRX`
- **THEN** `ZRX/USDT` is displayed on the current result page without scrolling
- **AND** it can be added or removed from that result row.

#### Scenario: Browse without a query

- **WHEN** no search query is present
- **THEN** pagination exposes every filtered result set
- **AND** changing pages does not scroll the result region.

### Requirement: Add-only selection with visible state

Manual selection SHALL add or remove items from explicit result actions while keeping counts and selected-state feedback current.

#### Scenario: Add and remove one item

- **WHEN** an unselected result is added
- **THEN** its accessible state and selected count update immediately
- **AND WHEN** the same result is removed
- **THEN** the count returns to its previous value.

#### Scenario: Empty search

- **WHEN** no catalog item matches the query
- **THEN** the workbench shows an explicit empty result with recovery guidance
- **AND** preserves the existing selection.

### Requirement: Whole-catalog selection with exceptions

The workbench SHALL support selecting an entire catalog in one action and SHALL represent subsequent removals as explicit exceptions.

#### Scenario: Select every symbol

- **WHEN** the administrator activates `Selecionar todos` for Symbols
- **THEN** the state reports `126/126`
- **AND** removing `ZRX/USDT` reports `125/126` and one exception.

### Requirement: Transactional apply and cancel

Catalog edits SHALL remain provisional until explicitly applied.

#### Scenario: Apply a changed selection

- **WHEN** the administrator applies a valid provisional selection
- **THEN** the compact summaries update
- **AND** preflight totals are recalculated from the committed selection.

#### Scenario: Cancel a changed selection

- **WHEN** the administrator cancels or presses Escape
- **THEN** provisional edits are discarded
- **AND** focus returns to the edit action that opened the workbench.

### Requirement: Accessible workbench interaction

The workbench SHALL expose a modal dialog name and description, semantic tabs, visible focus, a focus trap, live selection feedback, keyboard-operable controls, and effective targets of at least 44 × 44 px.

#### Scenario: Keyboard-only operation

- **WHEN** a keyboard user opens and traverses the workbench
- **THEN** focus remains inside the dialog until it closes
- **AND** Enter can add the first search result
- **AND** Escape closes without applying and restores focus.

### Requirement: Existing operational guardrails remain authoritative

The redesign SHALL NOT change preflight limits or silently start an invalid sweep.

#### Scenario: Large selection exceeds the sweep limit

- **WHEN** the applied catalog scope produces more than the allowed number of combinations
- **THEN** the existing preflight displays the over-limit result
- **AND** the start action remains unavailable until scope is reduced.

### Requirement: New draft does not pre-select catalog items

A new Discovery draft (first opening of Montar **or** the «Novo rascunho» action) SHALL NOT pre-select the first catalog templates or the first catalog symbols. Templates SHALL open with zero selected. Symbols SHALL open with zero selected. The operator MAY still mark templates and symbols afterwards using the same inline and advanced-edit controls as today.

#### Scenario: First opening has no templates or symbols selected

- **WHEN** the administrator opens `/combo/discovery` on a new draft
- **THEN** Templates reports 0 selected and shows no chips
- **AND** Symbols reports 0 selected and shows no chips

#### Scenario: Novo rascunho clears catalog selection

- **WHEN** the administrator activates «Novo rascunho»
- **THEN** Templates and Symbols return to zero selected, with no chips
- **AND** the operator can mark items afterwards as today

### Requirement: Three gap templates appear in Discovery catalog

The Discovery template catalog SHALL include three templates created through the existing template editor (not `lab_` files, not a one-off script, not a new engine): Canal Donchian + volume; Squeeze de Bollinger; Pullback média longa + RSI + ADX. Templates SHALL NOT pin a timeframe.

#### Scenario: Operator can pick the three gap templates

- **WHEN** the operator opens the Templates axis on Montar
- **THEN** Canal Donchian + volume, Squeeze de Bollinger and Pullback média longa + RSI + ADX are reachable for selection
- **AND** none of them is named with a `lab_` prefix

#### Scenario: Gap templates backtest on 4h 1h 15m

- **WHEN** each of the three templates is run on BTC/USDT at 4h, 1h and 15m
- **THEN** the backtest completes without error on each of those three timeframes

#### Scenario: An existing Discovery template also runs on 1h and 15m

- **WHEN** a template already offered by Discovery (for example Bollinger_Breakout) is run on BTC/USDT at 1h and at 15m
- **THEN** each backtest completes without error

### Requirement: Donchian breakout uses the preceding channel and existing volume confirmation

The Canal Donchian + volume template SHALL compare the evaluated candle's close strictly above the maximum high of the N immediately preceding candles, excluding the evaluated candle. It SHALL retain the existing strict volume confirmation, including the existing volume average period, multiplier and inclusion of the evaluated candle's volume. It SHALL require sufficient history and no open position to open a long trade. Validation SHALL cover 4h, 1h and 15m independently without pinning a template timeframe.

#### Scenario: Valid breakout produces a real long entry

- **WHEN** the template is backtested independently on 4h, 1h and 15m with N preceding candles, no open position, close above the preceding channel and volume confirmation satisfied
- **THEN** each backtest records an actual long trade with entry time and price, rather than merely returning signals or completing without error
- **AND** the decision is confirmed at the evaluated candle's close and execution occurs at the next candle's open using the existing execution convention

#### Scenario: Equal or lower close rejects entry

- **WHEN** volume confirmation is satisfied but the evaluated close equals or is below the preceding upper channel in each of 4h, 1h and 15m
- **THEN** no breakout entry is produced by that candle
- **AND** an intrabar high above the channel does not substitute for a close above it

#### Scenario: Missing volume confirmation rejects entry

- **WHEN** the evaluated close exceeds the preceding channel but volume does not strictly exceed the existing confirmation threshold in each of 4h, 1h and 15m
- **THEN** no breakout entry is produced by that candle

#### Scenario: Insufficient history cannot create entry

- **WHEN** fewer than N preceding candles are available, or the existing volume confirmation is not yet available
- **THEN** the template does not produce a breakout entry from an incomplete reference

#### Scenario: Configured channel length is respected

- **WHEN** the channel period is configured to a valid value other than the default
- **THEN** the comparison uses exactly that many preceding candles and continues to exclude the evaluated candle

### Requirement: Donchian entry decisions are causal and preserve unrelated behavior

The corrected template SHALL use only information available through the evaluated candle to decide entry. It SHALL preserve the existing Donchian indicator bands, exit condition, stop loss, other indicators, other templates, approval thresholds, fees, slippage and favorite promotion behavior.

#### Scenario: Future changes do not rewrite entry decisions

- **WHEN** OHLCV candles after the evaluated candle are changed in each of 4h, 1h and 15m
- **THEN** entry decisions through the evaluated candle and their next-candle entry signals are unchanged
- **AND** execution price remains unchanged when the next candle's opening price is held fixed; later exits and profits are not required to remain equal

#### Scenario: Evaluated high is excluded from its own reference

- **WHEN** only the evaluated candle's high changes while its close, volume and preceding history stay fixed
- **THEN** the preceding upper channel and that candle's breakout decision remain unchanged

#### Scenario: Shared indicator and other templates preserve their behavior

- **WHEN** identical data and parameters are evaluated before and after this correction
- **THEN** the Donchian upper, middle and lower indicator series and the template's exit condition are unchanged
- **AND** the other templates introduced by #1074 and an existing template such as Bollinger_Breakout preserve their indicator and signal outputs

#### Scenario: Existing catalog receives the corrected template

- **WHEN** the existing catalog seed loads the versioned export into an empty catalog or refreshes an already populated catalog
- **THEN** Canal Donchian + volume uses the corrected entry condition
- **AND** repeated loading preserves that condition without changing the other templates' definitions

