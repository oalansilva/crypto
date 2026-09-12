## ADDED Requirements

### Requirement: Easy metrics columns on the Decidir leaderboard

The Decidir leaderboard SHALL show six metric columns in the table, visible without expanding the row: Calmar, Max DD, Trades/cobertura, Sharpe, Win%, and CAGR. Sharpe SHALL be the persisted `sharpe_ratio` formatted with two decimal places. Win% SHALL be the persisted `win_rate` formatted as a percentage (hit rate), never the Trades/cobertura pair. CAGR SHALL be the scan's annualized return (`cagr`, the same value labelled «Retorno (CAGR)» in the promote dialog), never Favorites' accumulated Return. Sort controls SHALL remain Calmar and CAGR vs B&H only; the operator SHALL NOT gain sort-by Sharpe, Win%, or CAGR in this change.

#### Scenario: Six columns without expanding

- **GIVEN** the operator is on Decidir with a list of candidates
- **WHEN** they look at a row without clicking «+ detalhes»
- **THEN** that row shows Calmar, Max DD, Trades/cobertura, Sharpe, Win%, and CAGR in columns
- **AND** neighboring rows align those six values in the same columns

#### Scenario: CAGR is annualized scan return

- **GIVEN** a candidate whose promote dialog shows «Retorno (CAGR)» as a percentage
- **WHEN** the same row renders in the Decidir grid
- **THEN** the CAGR column shows that annualized percentage
- **AND** it does not show Favorites accumulated Return (example: `+47.916%`)

#### Scenario: Sort options stay Calmar and CAGR vs B&H

- **GIVEN** the Decidir sort control
- **WHEN** the operator opens it
- **THEN** the options remain Calmar and CAGR vs B&H
- **AND** Sharpe, Win%, and CAGR are not sort keys

### Requirement: Expanded details keep non-column extras

When the operator expands «+ detalhes» on a Decidir row, the expansion SHALL still expose Buy & Hold, delta versus B&H, Profit Factor, market, and evidence window. Sharpe, Win%, and CAGR SHALL NOT be the only place those three metrics appear; they SHALL already be in columns. The expansion MAY omit Sharpe, Win%, and CAGR to avoid duplicating the new columns.

#### Scenario: Plus details still has B&H PF and window

- **GIVEN** a Decidir row with «+ detalhes»
- **WHEN** the operator expands it
- **THEN** B&H, Δ B&H, PF, and the evidence window remain readable
- **AND** Sharpe, Win%, and CAGR were already visible as columns before the click

## MODIFIED Requirements

### Requirement: Communicate metric meaning accessibly

Headers SHALL expose full accessible names for Sharpe, Win%, CAGR (annualized scan return), `Maximum Drawdown` and, when those headers remain in expansion or elsewhere, `Buy and Hold`, `Delta versus Buy and Hold` and `Profit Factor`, through accessible text or `aria-label` (an abbreviation `title` alone is insufficient). Lifecycle colors SHALL use informational blue/yellow/neutrals, while green/red remain reserved for Long/Short and trading performance. Result-count changes SHALL use a polite live region. The educational disclaimer SHALL state that historical ranking is decision support, not a return guarantee.

#### Scenario: Expanded metric names are announced

- **GIVEN** a leaderboard with Sharpe, Win%, CAGR and `Max DD` column headers
- **WHEN** a screen reader traverses the column headers
- **THEN** each header exposes its full accessible name (Sharpe, Win rate, annualized CAGR of the scan, Maximum Drawdown)
- **AND** an abbreviation `title` attribute alone is not used as the accessible name

#### Scenario: Operational lifecycle colors do not reuse trading semantics

- **GIVEN** a sweep in progress, paused or cancelled state
- **WHEN** the lifecycle badge and progress bars are rendered
- **THEN** their colors are informational blue/yellow/neutrals
- **AND** green/red are reserved exclusively for Long/Short direction and trading performance indicators

#### Scenario: Result count changes are announced politely

- **GIVEN** a leaderboard showing filtered result counts
- **WHEN** a filter is applied or removed and the count changes
- **THEN** the change is announced through a polite live region without interrupting the screen reader

#### Scenario: Educational disclaimer is present

- **GIVEN** the leaderboard with historical ranking
- **WHEN** the administrator reviews the sweep results
- **THEN** an educational disclaimer is visible stating that the historical ranking is decision support and not a return guarantee
