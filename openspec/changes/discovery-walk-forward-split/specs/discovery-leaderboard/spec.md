## REMOVED Requirements

### Requirement: Discovery optimizer path SHALL persist ranking metrics without walk-forward split

**Reason:** Card #605 (pedido de Alan) torna o Discovery sempre walk-forward 70/30. O path legado sem `split_train_ratio` deixa de ser o contrato Discovery; ranking passa a ser in-sample.

**Migration:** Combinations call `run_optimization` with `split_train_ratio=0.7`. Ranking and the effective evidence window use the train split. Full-window discovery path is not used. Combo/other callers without split keep the #599 helper.

## MODIFIED Requirements

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

The default eligibility policy SHALL require at least `30` closed trades and `90%` candle coverage of the requested effective window. For Discovery walk-forward 70/30, the requested effective window SHALL be the in-sample (train) interval persisted on the result, not the unused sweep snapshot span. The thresholds SHALL be configuration/versioned and persisted with the result. Ineligible results SHALL remain inspectable with a `Baixa amostra` badge and reason, SHALL have no ranked position, and SHALL not be promotable until a later versioned reclassification makes them eligible. The Combo walk-forward GO/NO-GO profile (including the 100-trade in-sample floor) SHALL NOT replace this Discovery eligibility policy.

#### Scenario: Low sample candidate

- **WHEN** a successful result has 18 trades or 82% coverage
- **THEN** it is shown as `Baixa amostra`, receives no rank and cannot be promoted
- **AND** its metrics are not merged into eligible ordering

#### Scenario: Discovery eligibility uses in-sample sample quality

- **WHEN** a Discovery walk-forward result has at least 30 in-sample closed trades and at least 90% coverage of the train window
- **THEN** it MAY be eligible even if the holdout is `NO-GO` or `ERROR`
- **AND** it SHALL NOT be required to meet Combo walk-forward minima (100 in-sample trades / Sharpe 0.8) to rank

## ADDED Requirements

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
