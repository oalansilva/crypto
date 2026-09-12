## ADDED Requirements

### Requirement: Discovery Calmar uses calendar-window years

Discovery SHALL compute CAGR (and therefore Calmar = CAGR ÷ |Max DD|) with years equal to the calendar span of the evidence window: `(last_date − first_date) / 365`, using the persisted in-sample `[start_at, end_at)` (or the equity/candle timestamps of that same window). The system SHALL NOT treat each closed trade or each equity point as one day (`n_trades / 365` or `len(equity_curve) / 365`). Max DD SHALL stay a fraction 0–1 in the same unit as CAGR. Typical honest values remain visible with 2 decimal places (example: Calmar `1,20`).

#### Scenario: Thirty trades over three calendar years

- **GIVEN** a curve with 30 closed trades in an evidence window of ~3 years and a large compounded return
- **WHEN** the ranking calculates CAGR and Calmar
- **THEN** the years denominator is the calendar of the window (~3), not `31/365`
- **AND** the cell does not show a number on the order of `1e27` formatted as `pt-BR` money

#### Scenario: Honest finite Calmar stays visible

- **GIVEN** a candidate whose calendar Calmar is finite and reasonable (example: `1,2`)
- **WHEN** the row is rendered on Acompanhar parciais or Decidir
- **THEN** the Calmar cell shows the number with 2 decimal places in `pt-BR` (`1,20`)
- **AND** the cell is not `N/A`

### Requirement: Absurd or non-finite Calmar is N/A and does not take first place

Before persist and before `pt-BR` formatting, Discovery SHALL treat a Calmar that is non-finite (`NaN`, `±Inf`) or whose absolute value exceeds `1000` as missing. The stored ranking column SHALL be null and the cell SHALL render `N/A`. That row SHALL NOT compete for 1st place among eligible results (it sorts with other `N/A` values, after every finite Calmar in its walk-forward class). The same display sanitization SHALL apply when reading already-persisted finite absurd values (no backfill of sweep `#862f31de` is required). CAGR used for ranking SHALL likewise persist as null when non-finite or when its absolute value exceeds `100`.

#### Scenario: Persisted 1e27 is shown as N/A

- **GIVEN** a stored `calmar_ratio` on the order of `1e27` or any non-finite value
- **WHEN** Acompanhar parciais or Decidir format the Calmar cell
- **THEN** the cell is `N/A`
- **AND** the line does not occupy 1st place while any eligible finite Calmar exists in a higher walk-forward class or with a finite metric

#### Scenario: Ceiling leaves honest ~22 visible

- **GIVEN** a calendar-honest Calmar of ~22 (ALPHA/USDT after years = window/365)
- **WHEN** the value is persisted and formatted
- **THEN** the cell shows a finite number with 2 decimal places
- **AND** it is not replaced by `N/A`

### Requirement: Eligible ranking puts every GO above every NO-GO

Among results that are ranking-eligible (existing 30 trades / 90% coverage policy unchanged), the leaderboard and Acompanhar top-5 SHALL sort first by walk-forward class: `GO` above every non-`GO` (`NO-GO`, `ERROR`, or missing verdict). Only a `GO` SHALL occupy 1st place when at least one `GO` exists in the eligible set. Inside the same class, order remains selected metric descending (Calmar default, after calendar + ceiling), then closed trades descending, then stable `result_id` ascending. A `NO-GO` remains in the list with a visible seal and keeps a global rank below every `GO`. `Baixa amostra` / `Amostra insuficiente` stay unranked as today.

#### Scenario: ALPHA NO-GO sits below any GO

- **GIVEN** eligible `RS-B109ED2C80` ALPHA/USDT with walk-forward `NO-GO` and a calendar Calmar still high (~22)
- **AND** the same sweep has at least one eligible `GO`
- **WHEN** Acompanhar parciais and Decidir order the rows
- **THEN** every `GO` appears above that `NO-GO`
- **AND** the `NO-GO` remains in the list with its seal
- **AND** it is not «melhor da parcial» solely because Calmar is large

#### Scenario: Two NO-GOs keep Calmar then trades then id

- **GIVEN** two eligible `NO-GO` rows and no remaining `GO` above them
- **WHEN** they are ordered
- **THEN** the higher finite Calmar comes first
- **AND** equal Calmar defers to more closed trades, then lower `result_id`

### Requirement: Column copy distinguishes Calmar from return and trades from win rate

The Calmar column header SHALL expose an accessible name that states the metric is Calmar (CAGR of the calendar window ÷ Max DD), not return and not hit rate. The `Trades/cobertura` header SHALL expose the accessible name «negócios / cobertura» (closed trades and candle coverage). Visible column copy MAY add a short muted hint (`CAGR ÷ Max DD` / `negócios · velas`). `30 · 100%` SHALL remain the trades × coverage pair. Win rate, when shown, SHALL stay in «+ detalhes», never in that column.

#### Scenario: Screen reader names Calmar and coverage

- **GIVEN** a leaderboard or parciais table
- **WHEN** a screen reader traverses the column headers
- **THEN** Calmar is announced as Calmar (annual calendar CAGR ÷ Max DD), not as return
- **AND** `Trades/cobertura` is announced as negócios / cobertura
- **AND** an abbreviation `title` alone is not the accessible name

#### Scenario: Thirty times one hundred percent is not win rate

- **GIVEN** a row showing `30 · 100%` in `Trades/cobertura`
- **WHEN** the operator reads the column
- **THEN** the header/aria identify negócios and cobertura
- **AND** win rate is not that cell (it remains in «+ detalhes» when present)

## MODIFIED Requirements

### Requirement: Rank eligible results deterministically

The leaderboard SHALL support Calmar (default) and CAGR delta versus Buy & Hold. Eligible results SHALL sort first by walk-forward class (`GO` above every non-`GO`), then by selected metric descending among finite values, then closed trades descending, then stable `result_id` ascending. Negative finite values remain ranked below higher finite values of the same class. `N/A` (missing, non-finite, or abs(Calmar) > 1000) sorts after every finite value of the same class and uses the same trades/ID tie-breakers; it SHALL NOT take 1st place. Rank is global within the unfiltered eligible result set; filters and pagination SHALL preserve that global rank rather than renumbering the visible subset.

#### Scenario: Trades take precedence over stable IDs

- **WHEN** `RS-1048` and `RS-1049` have equal selected metric, `RS-1048` has 44 trades and `RS-1049` has 45 trades
- **THEN** their order is `RS-1049`, then `RS-1048`, even though `RS-1048` has the lower stable ID

#### Scenario: Stable ID is the final tie-breaker

- **WHEN** two eligible results have equal selected metric and equal closed trades
- **THEN** the lower stable `result_id` sorts first

#### Scenario: Metric divergence, negative and N/A fixtures

- **WHEN** Calmar order differs from delta-B&H order and the set includes negative and `N/A` selected metrics
- **THEN** each sort returns the exact expected stable ID sequence from class/metric/trades/ID rules
- **AND** negative finite precedes `N/A` inside the same walk-forward class

#### Scenario: Stable pagination and filtering

- **WHEN** a user changes pages or applies/removes an AND filter
- **THEN** no eligible result is duplicated or omitted
- **AND** each visible result retains its global rank from the selected sort

#### Scenario: GO class precedes NO-GO class

- **WHEN** an eligible `GO` has Calmar `1,20` and an eligible `NO-GO` has Calmar `22,00`
- **THEN** the `GO` is ordered first
- **AND** the `NO-GO` remains listed with a rank below every `GO`

### Requirement: Communicate metric meaning accessibly

Headers SHALL expose full accessible names for `Calmar` (CAGR of the calendar window ÷ Max DD, not return), `Trades/cobertura` (negócios fechados / cobertura de velas, not win rate), `Buy and Hold`, `Delta versus Buy and Hold`, `Maximum Drawdown` and `Profit Factor` through accessible text or `aria-label` (an abbreviation `title` alone is insufficient). Lifecycle colors SHALL use informational blue/yellow/neutrals, while green/red remain reserved for Long/Short and trading performance. Walk-forward `GO` SHALL use informational blue; `NO-GO` SHALL use danger (rejection), distinct from amber sample badges. Result-count changes SHALL use a polite live region. The educational disclaimer SHALL state that historical ranking is decision support, not a return guarantee.

#### Scenario: Expanded metric names are announced

- **GIVEN** a leaderboard with `Calmar`, `Trades/cobertura`, `B&H`, `Δ B&H`, `Max DD` and `PF` column headers
- **WHEN** a screen reader traverses the column headers
- **THEN** each header exposes its full accessible name (`Calmar (CAGR anual do calendário ÷ Max DD)`, `negócios / cobertura`, `Buy and Hold`, `Delta versus Buy and Hold`, `Maximum Drawdown`, `Profit Factor`)
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
