# discovery-leaderboard Specification

## Purpose
TBD - created by archiving change card-469-varredura-backtest. Update Purpose after archive.
## Requirements
### Requirement: Persist comparable optimizer outputs and evidence

For each successful combination the system SHALL persist `sweep_id`, stable `result_id`, template/version, symbol, timeframe, direction, effective parameters, effective `start_at`/`end_at`, candle source/version, fees and slippage assumptions, trade count, coverage ratio and normalized metrics. All comparison windows SHALL use timezone `UTC` and half-open interval `[start_at, end_at)`. Mapping SHALL be explicit: CAGR from optimizer annualized return; Buy & Hold CAGR from the same asset/candles/window as a long-only benchmark (also for short candidates); delta as strategy CAGR minus B&H CAGR in percentage points; Calmar from CAGR divided by absolute optimizer maximum drawdown; maximum drawdown from optimizer equity drawdown; Sharpe from optimizer risk-adjusted return; Profit Factor from gross profit/gross loss; win rate from winning/closed trades; trades from closed-trade count. Missing/non-finite values SHALL be `N/A`, never zero.

For each candle source/version and timeframe, the system SHALL persist the versioned expected 24×7 market calendar and `expected_candles` for `[start_at, end_at)`. `observed_valid_candles` SHALL count only unique, ordered, source-valid candles inside that interval after deterministic duplicate/out-of-order handling. Gaps SHALL NOT be forward-filled for coverage; they reduce coverage using `coverage = observed_valid_candles / expected_candles`. Ranking eligibility SHALL compare results only when timezone, interval convention, calendar version, source/version and cost assumptions are exposed; a calendar/source change creates new evidence rather than silently mixing denominators.

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

### Requirement: Gate ranking and promotion eligibility by sample quality

The default eligibility policy SHALL require at least `30` closed trades and `90%` candle coverage of the requested effective window. The thresholds SHALL be configuration/versioned and persisted with the result. Ineligible results SHALL remain inspectable with a `Baixa amostra` badge and reason, SHALL have no ranked position, and SHALL not be promotable until a later versioned reclassification makes them eligible.

#### Scenario: Low sample candidate

- **WHEN** a successful result has 18 trades or 82% coverage
- **THEN** it is shown as `Baixa amostra`, receives no rank and cannot be promoted
- **AND** its metrics are not merged into eligible ordering

### Requirement: Rank eligible results deterministically

The leaderboard SHALL support Calmar (default) and CAGR delta versus Buy & Hold. Eligible finite values sort by selected metric descending, then closed trades descending, then stable `result_id` ascending. Negative finite values remain ranked below higher finite values. `N/A` sorts after every finite value and uses the same trades/ID tie-breakers. Rank is global within the unfiltered eligible result set; filters and pagination SHALL preserve that global rank rather than renumbering the visible subset.

#### Scenario: Trades take precedence over stable IDs

- **WHEN** `RS-1048` and `RS-1049` have equal selected metric, `RS-1048` has 44 trades and `RS-1049` has 45 trades
- **THEN** their order is `RS-1049`, then `RS-1048`, even though `RS-1048` has the lower stable ID

#### Scenario: Stable ID is the final tie-breaker

- **WHEN** two eligible results have equal selected metric and equal closed trades
- **THEN** the lower stable `result_id` sorts first

#### Scenario: Metric divergence, negative and N/A fixtures

- **WHEN** Calmar order differs from delta-B&H order and the set includes negative and `N/A` selected metrics
- **THEN** each sort returns the exact expected stable ID sequence from metric/trades/ID rules
- **AND** negative finite precedes `N/A`

#### Scenario: Stable pagination and filtering

- **WHEN** a user changes pages or applies/removes an AND filter
- **THEN** no eligible result is duplicated or omitted
- **AND** each visible result retains its global rank from the selected sort

### Requirement: Filter and page within one selected sweep

Leaderboard queries SHALL require one `sweep_id`, combine symbol/timeframe/direction/eligibility filters with AND semantics, return filtered and unfiltered totals, and use deterministic cursor/page ordering. The UI SHALL provide search and pagination appropriate to up to 30 templates, 126 symbols and hundreds of results. A run selector SHALL navigate historical sweeps without mixing progress/snapshot counters.

#### Scenario: Select a historical run

- **WHEN** the administrator changes the run selector
- **THEN** loading blocks promotion and then heading, lifecycle, snapshot metadata, counts, rows, promotion dialog and success feedback all atomically identify the selected `sweep_id`
- **AND** an active sweep remains separately identified

### Requirement: Communicate metric meaning accessibly

Headers SHALL expose full accessible names for `Buy and Hold`, `Delta versus Buy and Hold`, `Maximum Drawdown` and `Profit Factor` through accessible text or `aria-label` (an abbreviation `title` alone is insufficient). Lifecycle colors SHALL use informational blue/yellow/neutrals, while green/red remain reserved for Long/Short and trading performance. Result-count changes SHALL use a polite live region. The educational disclaimer SHALL state that historical ranking is decision support, not a return guarantee.

#### Scenario: Expanded metric names are announced

- **GIVEN** a leaderboard with `B&H`, `Δ B&H`, `Max DD` and `PF` column headers
- **WHEN** a screen reader traverses the column headers
- **THEN** each header exposes its full accessible name (`Buy and Hold`, `Delta versus Buy and Hold`, `Maximum Drawdown`, `Profit Factor`)
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

