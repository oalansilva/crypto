## ADDED Requirements

### Requirement: Shared Favorites indicator names and order on the Decidir grid

The Decidir leaderboard SHALL show the shared Favorites indicators with the same names and the same left-to-right order: Sharpe, Trades, Win%, Return, Max DD. Discovery-only extras SHALL follow that block: Calmar (visible subtext `CAGR ÷ Max DD`) then CAGR anualizado (own name, last metric). Return SHALL exist as its own column. CAGR anualizado SHALL NOT use the name Return and SHALL NOT occupy Return's slot. Trades SHALL be named Trades; candle coverage, if shown, SHALL be subtext of Trades, never the column name. Rank, candidate identity, and Ação SHALL remain. The grid SHALL NOT copy Favorites columns Sel, Tier, Telegram, Symbol, Stop, PF, or SQN. Numbers MAY differ from Favorites; this requirement aligns names and order, not values. All seven metric columns SHALL be visible without expanding «+ detalhes».

#### Scenario: Operator rereads Favorites names in order

- **GIVEN** Favorites shows Sharpe, Trades, Win%, Return, Max DD
- **WHEN** the administrator opens Decidir
- **THEN** those five names appear in that order before Calmar and CAGR anualizado
- **AND** a Return column exists
- **AND** CAGR anualizado is the last metric and is not labelled Return

#### Scenario: Same setup may keep different numbers

- **GIVEN** the same setup has Return +16.951% in Favorites and CAGR 3,7% in Discovery
- **WHEN** this change is in place
- **THEN** names and order are aligned
- **AND** it is not a failure that the numbers remain different

## MODIFIED Requirements

### Requirement: Communicate metric meaning accessibly

Headers SHALL expose full accessible names for Sharpe, Trades, Win%, Return (compound return of the scan evidence window), Maximum Drawdown, Calmar (calendar CAGR ÷ Max DD), and CAGR anualizado (annualized scan return), and, when those headers remain in expansion or elsewhere, Buy and Hold, Delta versus Buy and Hold and Profit Factor, through accessible text or `aria-label` (an abbreviation `title` alone is insufficient). Lifecycle colors SHALL use informational blue/yellow/neutrals, while green/red remain reserved for Long/Short and trading performance. Result-count changes SHALL use a polite live region. The educational disclaimer SHALL state that historical ranking is decision support, not a return guarantee.

#### Scenario: Expanded metric names are announced

- **GIVEN** a leaderboard with Sharpe, Trades, Win%, Return, Max DD, Calmar and CAGR anualizado column headers
- **WHEN** a screen reader traverses the column headers
- **THEN** each header exposes its full accessible name (Sharpe, Trades, Win rate, Return of the scan window, Maximum Drawdown, Calmar as CAGR ÷ Max DD, annualized CAGR of the scan)
- **AND** an abbreviation `title` attribute alone is not used as the accessible name
- **AND** Return is not announced as CAGR
- **AND** CAGR anualizado is not announced as Return

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

### Requirement: Column copy distinguishes Calmar from return and trades from win rate

The Calmar column header SHALL expose an accessible name that states the metric is Calmar (CAGR of the calendar window ÷ Max DD), not Return and not hit rate. The Trades header SHALL expose the accessible name Trades (closed trades). Visible column copy MAY add a short muted hint for coverage (`cobertura` / `velas`). Coverage SHALL NOT rename the column to `Trades/cobertura`. Win% SHALL stay in its own column. Return SHALL stay in its own column and SHALL NOT reuse the CAGR anualizado value or name.

#### Scenario: Screen reader names Calmar and Trades

- **GIVEN** a leaderboard or parciais table
- **WHEN** a screen reader traverses the column headers
- **THEN** Calmar is announced as Calmar (annual calendar CAGR ÷ Max DD), not as Return
- **AND** Trades is announced as Trades
- **AND** an abbreviation `title` alone is not the accessible name

#### Scenario: Coverage is subtext of Trades not win rate

- **GIVEN** a row showing 30 closed trades and 100% candle coverage
- **WHEN** the operator reads the Trades column
- **THEN** the header name is Trades
- **AND** coverage is subtext, not the column name
- **AND** win rate is not that cell

### Requirement: Easy metrics columns on the Decidir leaderboard

The Decidir leaderboard SHALL show seven metric columns in the table, visible without expanding the row, in this order: Sharpe, Trades, Win%, Return, Max DD, Calmar, CAGR anualizado. Sharpe SHALL be the persisted `sharpe_ratio` formatted with two decimal places. Win% SHALL be the persisted `win_rate` formatted as a percentage (hit rate), never the Trades cell. Return SHALL be the compound return of the scan evidence window (`total_return` / `total_return_pct` from the persisted result metrics), never `cagr` and never Favorites' stored Return. CAGR anualizado SHALL be the scan's annualized return (`cagr`, the same value labelled «Retorno (CAGR)» in the promote dialog). Sort controls SHALL remain Calmar and CAGR vs B&H only; the operator SHALL NOT gain sort-by Sharpe, Win%, Return, or CAGR anualizado in this change.

#### Scenario: Seven columns without expanding

- **GIVEN** the operator is on Decidir with a list of candidates
- **WHEN** they look at a row without clicking «+ detalhes»
- **THEN** that row shows Sharpe, Trades, Win%, Return, Max DD, Calmar, and CAGR anualizado in that order
- **AND** neighboring rows align those seven values in the same columns

#### Scenario: Return is not CAGR

- **GIVEN** a candidate whose CAGR anualizado is 3,7%
- **WHEN** the same row renders in the Decidir grid
- **THEN** the Return column shows the window compound return, not 3,7%
- **AND** CAGR anualizado remains the last metric with its own name

#### Scenario: Sort options stay Calmar and CAGR vs B&H

- **GIVEN** the Decidir sort control
- **WHEN** the operator opens it
- **THEN** the options remain Calmar and CAGR vs B&H
- **AND** Sharpe, Win%, Return, and CAGR anualizado are not sort keys

### Requirement: Expanded details keep non-column extras

When the operator expands «+ detalhes» on a Decidir row, the expansion SHALL still expose Buy & Hold, delta versus B&H, Profit Factor, market, and evidence window. Sharpe, Win%, Return, and CAGR anualizado SHALL already be in columns. The expansion MAY omit those column metrics to avoid duplicating them.

#### Scenario: Plus details still has B&H PF and window

- **GIVEN** a Decidir row with «+ detalhes»
- **WHEN** the operator expands it
- **THEN** B&H, Δ B&H, PF, and the evidence window remain readable
- **AND** Sharpe, Trades, Win%, Return, Max DD, Calmar, and CAGR anualizado were already visible as columns before the click
