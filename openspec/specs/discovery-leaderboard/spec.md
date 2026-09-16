# discovery-leaderboard Specification

## Purpose
TBD - created by archiving change card-469-varredura-backtest. Update Purpose after archive.
## Requirements
### Requirement: Persist comparable optimizer outputs and evidence

For each successful combination the system SHALL persist `sweep_id`, stable `result_id`, template/version, symbol, timeframe, direction, effective parameters, effective `start_at`/`end_at`, candle source/version, fees and slippage assumptions, trade count, coverage ratio and normalized metrics. All comparison windows SHALL use timezone `UTC` and half-open interval `[start_at, end_at)`. Mapping SHALL be explicit: CAGR from optimizer annualized return; Buy & Hold CAGR from the same asset/candles/window as a long-only benchmark (also for short candidates); delta as strategy CAGR minus B&H CAGR in percentage points; Calmar from CAGR divided by absolute maximum drawdown; maximum drawdown from optimizer equity drawdown; Sharpe from optimizer risk-adjusted return; Profit Factor from gross profit/gross loss; win rate from winning/closed trades; trades from closed-trade count. Missing/non-finite values SHALL be `N/A`, never zero.

For each candle source/version and timeframe, the system SHALL persist the versioned expected 24×7 market calendar and `expected_candles` for `[start_at, end_at)`. `observed_valid_candles` SHALL count only unique, ordered, source-valid candles inside that interval after deterministic duplicate/out-of-order handling. Gaps SHALL NOT be forward-filled for coverage; they reduce coverage using `coverage = observed_valid_candles / expected_candles`. Ranking eligibility SHALL compare results only when timezone, interval convention, calendar version, source/version and cost assumptions are exposed; a calendar/source change creates new evidence rather than silently mixing denominators.

When Discovery runs with walk-forward 70/30, the effective evidence window `[start_at, end_at)` SHALL be the in-sample (train) window, not the sweep snapshot period. Expected candles, observed candles, coverage, trade count and ranking metrics SHALL be computed for that train interval. Buy & Hold SHALL use the same train close series.

#### Scenario: Reconstruct without rerunning

- **WHEN** all persisted results of a sweep are read
- **THEN** metrics, assumptions and evidence window reconstruct the leaderboard without invoking the optimizer

#### Scenario: Short benchmark

- **WHEN** the result direction is `short`
- **THEN** B&H remains the asset's long-only market benchmark over identical candles/window
- **AND** copy makes that convention explicit

#### Scenario: UTC half-open window and candle gaps

- **WHEN** a `4h` result covers a UTC `[start_at, end_at)` whose versioned 24×7 calendar expects `N` candles and the source has gaps
- **THEN** the persisted denominator is `N`, the numerator counts only valid unique candles, and coverage is `observed_valid_candles / N`
- **AND** missing candles are not forward-filled to improve eligibility

#### Scenario: Discovery walk-forward uses the train window as evidence

- **WHEN** a Discovery combination completes with split 70/30
- **THEN** persisted `start_at`/`end_at`/`expected_candles`/`coverage`/`trades_count` describe the in-sample window
- **AND** they SHALL NOT use the unused holdout span as the coverage denominator

### Requirement: Gate ranking and promotion eligibility by sample quality

The default eligibility policy SHALL require at least `30` closed trades and `90%` candle coverage of the requested effective window. For Discovery walk-forward 70/30, the requested effective window SHALL be the in-sample (train) interval persisted on the result, not the unused sweep snapshot span. The thresholds SHALL be configuration/versioned and persisted with the result. Ineligible optimizer results SHALL remain inspectable with a `Baixa amostra` badge and reason, SHALL have no ranked position, and SHALL not be promotable until a later versioned reclassification makes them eligible. Listing-gate results SHALL use `eligibility=insufficient_sample` and the visible badge `Amostra insuficiente`; they SHALL NOT reuse the `Baixa amostra` badge or `low_sample` eligibility. The Combo walk-forward GO/NO-GO profile (including the 100-trade in-sample floor) SHALL NOT replace this Discovery eligibility policy.

#### Scenario: Low sample candidate

- **WHEN** a successful result has 18 trades or 82% coverage
- **THEN** it is shown as `Baixa amostra`, receives no rank and cannot be promoted
- **AND** its metrics are not merged into eligible ordering

#### Scenario: Discovery eligibility uses in-sample sample quality

- **WHEN** a Discovery walk-forward result has at least 30 in-sample closed trades and at least 90% coverage of the train window
- **THEN** it MAY be eligible even if the holdout is `NO-GO` or `ERROR`
- **AND** it SHALL NOT be required to meet Combo walk-forward minima (100 in-sample trades / Sharpe 0.8) to rank

#### Scenario: Insufficient sample is not baixa amostra

- **WHEN** a result was cut before the optimizer because train bars < 30
- **THEN** the visible badge is `Amostra insuficiente`
- **AND** the badge is not `Baixa amostra`
- **AND** the result is not ranked and not promotable

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

### Requirement: Filter and page within one selected sweep

Leaderboard queries SHALL require one `sweep_id`, combine symbol/timeframe/direction/eligibility filters with AND semantics, return filtered and unfiltered totals, and use deterministic cursor/page ordering. The default list SHALL omit results whose `dedup_state` is `discarded`. Rank SHALL be computed among remaining eligible results. The UI SHALL provide search and pagination appropriate to up to 30 templates, 126 symbols and hundreds of results. A run selector SHALL navigate historical sweeps without mixing progress/snapshot counters.

#### Scenario: Select a historical run

- **WHEN** the administrator changes the run selector
- **THEN** loading blocks promotion and then heading, lifecycle, snapshot metadata, counts, rows, promotion dialog and success feedback all atomically identify the selected `sweep_id`
- **AND** an active sweep remains separately identified

#### Scenario: Discarded rows omitted from default list

- **WHEN** a sweep has a discarded result and the administrator opens the default leaderboard
- **THEN** that `result_id` is absent
- **AND** remaining rows keep stable ordering among themselves

### Requirement: Action column always exposes promote and discard when allowed

Each visible non-promoted row whose eligibility is `eligible` or `low_sample` SHALL show a Promote control (enabled only when unique and eligible; otherwise visible and disabled with reason) **and** a Discard control. An `already_promoted` row SHALL show the promoted state and SHALL NOT show Discard. Promote MUST NOT be hidden solely because `low_sample` eligibility failed. A row with `eligibility=insufficient_sample` SHALL NOT show a Promote control (no CTA) and SHALL keep Discard when discard is otherwise allowed.

#### Scenario: Low sample still shows both actions

- **WHEN** a row is `Baixa amostra`
- **THEN** Promote is visible and disabled with the sample reason
- **AND** Excluir is visible and enabled

#### Scenario: Insufficient sample has no promote CTA

- **WHEN** a row is `Amostra insuficiente`
- **THEN** no Promover control is rendered
- **AND** the operator cannot promote that row
- **AND** Excluir remains available

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

### Requirement: Discovery leaderboard ranking SHALL use walk-forward in-sample metrics

Discovery SHALL persist ranking metrics from the in-sample (train) window of walk-forward 70/30, not from a full-window backtest without split. CAGR, Calmar, Buy & Hold CAGR, delta versus B&H, Sharpe, profit factor, win rate, drawdown and closed-trade count SHALL map from the optimizer in-sample outputs after worker sanitization. When in-sample closed trades are zero or values are non-finite, ranking fields SHALL remain `N/A` (null), not numeric zero substitutes — including when the optimizer in-sample helper emitted `0.0`. If the holdout path errors and in-sample trades exist but CAGR is missing, the worker SHALL enrich in-sample ranking before persist. The persisted `metrics` JSON SHALL include `split_train_ratio=0.7` and `split_applied`. When the optimizer returns `oos_metrics` and/or `oos_verdict` (including `status=ERROR`), those objects SHALL be stored inside `metrics`. Holdout verdict SHALL NOT by itself change Discovery eligibility or promotion in this change.

#### Scenario: Combination with in-sample trades gets ranking metrics

- **WHEN** a discovery combination completes with at least one closed in-sample trade and finite drawdown
- **THEN** the persisted `DiscoveryResult` includes finite `cagr`, `calmar_ratio`, `benchmark_cagr`, and `delta_cagr_vs_bh` from the train window
- **AND** `metrics` contains `split_train_ratio` of `0.7`

#### Scenario: Zero in-sample trades keep N/A even if optimizer emitted zero

- **WHEN** a discovery combination completes with zero closed in-sample trades and `best_metrics.cagr` is `0.0`
- **THEN** `cagr`, `calmar_ratio`, `benchmark_cagr`, and `delta_cagr_vs_bh` are persisted as null
- **AND** Sharpe/profit factor/win rate are not coerced to fake ranking values beyond their own semantics

#### Scenario: Holdout evidence is stored without blocking rank

- **WHEN** the optimizer returns `oos_metrics` and `oos_verdict`
- **THEN** those objects are stored inside `DiscoveryResult.metrics`
- **AND** a `NO-GO` holdout does not by itself mark the row ineligible or unpromotable under existing Discovery eligibility rules

#### Scenario: Holdout ERROR still persists in-sample ranking

- **WHEN** the optimizer returns `oos_verdict.status=ERROR` (or equivalent) and the in-sample backtest closed at least one trade
- **THEN** `metrics` stores that verdict
- **AND** ranking CAGR/Calmar/B&H are still persisted from the in-sample trades when computable

### Requirement: Persist inspectable insufficient-sample results

For each combination cut by the listing gate the system SHALL persist a `DiscoveryResult` with `eligibility=insufficient_sample` (never `low_sample` or `eligible`), `rank` null, and ranking metrics (`calmar_ratio`, `max_drawdown`, `trades_count`, coverage used for ranking) stored as null so the UI shows `N/A`. The result SHALL remain in the default Decidir list (not omitted as discarded). It SHALL NOT receive a ranked position and SHALL NOT occupy Acompanhar top-5 partials.

#### Scenario: Short listing appears on Decidir without rank

- **WHEN** a combination settles as `insufficient_sample`
- **THEN** a result row exists for that symbol × timeframe × template
- **AND** `eligibility` is `insufficient_sample`
- **AND** rank is null and Calmar/drawdown/trades are null

#### Scenario: Insufficient sample stays out of top-5

- **WHEN** Acompanhar requests locked top-5 partials
- **THEN** no `insufficient_sample` row is included
- **AND** eligible (and, if no eligible, existing `low_sample`) ordering is unchanged

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

### Requirement: Grid tells the truth after a favorite is deleted

On `/combo/discovery`, Decidir and Acompanhar (when the same row is still visible) SHALL show the same current classification. After the referenced favorite has been deleted, an eligible row that used to show **Já existe** / **Equivale ao favorito ativo N** or **Favorito tier 3** SHALL show **Promover** (if the rest of the row still allows it). That row SHALL NOT show **Já existe**, SHALL NOT show **Equivale ao favorito ativo N**, SHALL NOT show **Favorito tier 3**, and SHALL NOT show a note that it used to be a favorite. The row SHALL remain on the sweep; deleting the favorite SHALL NOT hide it. A row whose equivalent favorite still exists SHALL keep **Já existe** / **Equivale ao favorito ativo N**. **Excluir** on the grid still discards only that sweep result and SHALL NOT delete a favorite.

#### Scenario: Orphan Já existe row returns to Promover

- **GIVEN** a completed sweep whose row showed **Já existe** / **Equivale ao favorito ativo N**
- **AND** favorite N has been deleted
- **WHEN** the administrator opens Decidir on that sweep
- **THEN** the row shows **Promover** if otherwise eligible
- **AND** it does not show **Já existe**
- **AND** it does not show **Equivale ao favorito ativo N**
- **AND** it does not show a historical-favorite note
- **AND** the row is still on the sweep

#### Scenario: Orphan Favorito tier 3 row returns to Promover

- **GIVEN** a sweep row that showed **Favorito tier 3** because it created favorite N
- **AND** favorite N has been deleted
- **WHEN** the administrator opens that sweep
- **THEN** the row does not show **Favorito tier 3**
- **AND** it shows **Promover** if otherwise eligible

#### Scenario: Acompanhar matches Decidir

- **GIVEN** the same orphan or live-duplicate row is still visible on Acompanhar
- **WHEN** the administrator opens Acompanhar
- **THEN** that surface shows the same Promover / Já existe / Favorito tier 3 truth as Decidir

#### Scenario: Live favorite is not a regression

- **GIVEN** a favorite that still exists
- **WHEN** an equivalent candidate is shown
- **THEN** the row still shows **Já existe** and **Equivale ao favorito ativo N**

### Requirement: Acompanhar parciais show the candidate before the run closes

While the active Discovery sweep is still non-terminal, Acompanhar locked top-5 parciais SHALL show a candidate row as soon as that result exists for **this** sweep. The empty copy **Parciais ainda carregando** SHALL NOT remain in that state. The Acompanhar progress counter SHALL NOT display 0 of N when this sweep has already processed combinations. Parciais SHALL keep being a top-5 of this sweep (no pagination, no becoming Decidir). Montar SHALL keep Preflight and Rascunho without this card's partials delta.

#### Scenario: Candidate exists mid-run

- **GIVEN** a non-terminal sweep the Acompanhar is following, and a ranked result for that sweep already exists
- **WHEN** the operator stays on Acompanhar without reloading
- **THEN** the parciais table shows that candidate line
- **AND** the phrase «Parciais ainda carregando» is not shown

#### Scenario: Progress is not stuck at zero after processing

- **GIVEN** the active sweep has `processed > 0`
- **WHEN** Acompanhar shows the progress of that sweep
- **THEN** the counter is not 0 de N
- **AND** the displayed processed count matches this sweep, not another run in Histórico

