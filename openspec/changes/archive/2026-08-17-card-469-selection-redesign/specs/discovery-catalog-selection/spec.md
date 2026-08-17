# Discovery catalog selection

## ADDED Requirements

### Requirement: Compact catalog summaries

The Discovery draft SHALL represent Templates and Symbols as compact selection summaries instead of rendering the catalog as an open vertical list in the form.

#### Scenario: Default draft

- **WHEN** the administrator opens `/combo/discovery`
- **THEN** each catalog summary shows the selected count, representative selected items, and an explicit edit action
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
