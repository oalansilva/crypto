## MODIFIED Requirements

### Requirement: Compact catalog summaries

The Discovery draft SHALL represent Templates and Symbols as compact selection summaries instead of rendering the catalog as an open vertical list in the form.

#### Scenario: Default draft

- **WHEN** the administrator opens `/combo/discovery` on a new draft
- **THEN** each catalog summary shows the selected count, an explicit edit action, and representative selected items only when at least one item is selected
- **AND** a new draft shows count 0, no chips, and empty selection for Templates and for Symbols
- **AND** timeframe, direction, period, ranking, preflight, active sweep, history, and leaderboard retain their existing hierarchy.

## ADDED Requirements

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
