## MODIFIED Requirements

### Requirement: The multi-day Jev ruler is read-only and precedes every threshold change

The Farol SHALL provide `scripts/scalp_jev_eval.py`, a **read-only** evaluation instrument over the #1015 diagnostic log (`backend/scalp_jev_diagnostic.log`, overridable by `SCALP_JEV_LOG_FILE`) joined with realized prices from the existing OHLCV storage. The instrument SHALL report: forecast versus realized with **non-overlapping** windows, segmentation by regime, net expectancy per bucket of `score` and of `confidence`, and the calibration curve (`confidence` → |realized|). It SHALL also report the matched-bias benchmark, the predictive contribution, the BUY fraction, signal accuracy beside buy-and-hold accuracy, the in-use geometry's break-even win rate with and without cost beside the realized hit by barrier, and break-even, realized hit and net expectancy for each candidate horizon. It SHALL NOT write product tables, trading state, an applied confidence version, or any database. It SHALL run before any change of the confidence policy or of the barrier geometry. An insufficient sample, an unverified sample, or a failed measurement SHALL be declared as such instead of being concluded. Adopting a geometry SHALL NOT happen inside this instrument.

The matched-bias benchmark SHALL compare the signal with (a) buy-and-hold of the same asset and (b) a random rule with the same directional bias (the same BUY fraction), using the same round-trip cost on all three. Predictive contribution SHALL be the signal's mean net return minus the random rule's mean net return, in bp, reported per confidence band, per regime and per horizon. Buy-and-hold SHALL be reported beside that contribution and SHALL NOT be substituted for it. The random draw SHALL be reproducible from a seed recorded in the report.

When `--regime-boundary-bp` is absent, the ruler SHALL read `SCALP_REGIME_BOUNDARY_BP` from the same runtime configuration consumed by the entry decision. An explicit CLI value SHALL be passed into the report; when it differs from the environment, the ruler SHALL warn that the decision uses the environment value. The summary and report SHALL include the actual period containing windows with realized prices, the number of priced windows, and SHALL identify these as historical evaluation windows rather than executed trades.

For the geometry in use the report SHALL show, side by side, the break-even win rate with cost and without cost, and the realized hit split by target, stop and time exit. Break-even without cost SHALL be `|stop| / (|target| + |stop|)`. Break-even with cost SHALL be `(2 × fee per leg + |stop|) / (|target| + |stop|)`. The report SHALL propose an alternative geometry (target, stop or horizon) whose break-even with cost is **below** the realized hit, or SHALL declare that none can. Candidate horizons SHALL be 15 min, 1 h, 4 h and 24 h, measured with the finest OHLCV timeframe already stored that fits inside the horizon. A 15 min horizon that cannot resolve a barrier SHALL be reported as barrier indeterminate, not as a hit rate of zero. No geometry SHALL be adopted without the report. When no candidate geometry or horizon beats its break-even, the report SHALL declare the strategy **não operável** and SHALL NOT adopt any parameter. This instrument SHALL NOT write target, stop, horizon or size.

#### Scenario: Multi-day report is produced from the diagnostic log

- **WHEN** the ruler runs over a multi-day diagnostic log with the realized prices available
- **THEN** the report SHALL show forecast versus realized on non-overlapping windows, segmented by regime
- **AND** SHALL show net expectancy per `score` and `confidence` bucket, and the calibration curve

#### Scenario: Matched-bias benchmark is not the market drift

- **WHEN** the ruler reports a measured sample
- **THEN** the report SHALL show predictive contribution (signal minus the random same-bias rule) per confidence band, per regime and per horizon
- **AND** SHALL show buy-and-hold separately from that contribution
- **AND** SHALL show the BUY fraction and signal accuracy beside buy-and-hold accuracy

#### Scenario: Break-even sits beside the realized barrier hit

- **WHEN** the ruler reports the geometry in use
- **THEN** the report SHALL show the break-even win rate with cost and without cost beside the realized hit by target, stop and time exit

#### Scenario: Candidate horizons are measured

- **WHEN** the ruler builds the geometry section
- **THEN** the report SHALL show break-even, realized hit and net expectancy for 15 min, 1 h, 4 h and 24 h
- **AND** a 15 min window whose candle cannot contain the barrier SHALL be barrier indeterminate, not a zero hit rate

#### Scenario: No candidate beats break-even

- **WHEN** no candidate geometry or horizon has a break-even with cost below the realized hit
- **THEN** the report SHALL declare the strategy não operável
- **AND** SHALL NOT adopt any parameter, including a confidence policy

#### Scenario: An alternative is proposed and not adopted

- **WHEN** a candidate geometry or horizon has a break-even with cost below the realized hit
- **THEN** the report SHALL propose that alternative
- **AND** the ruler SHALL NOT write target, stop, horizon or size

#### Scenario: Insufficient sample is declared, not concluded

- **WHEN** the available log does not cover enough non-overlapping windows for a bucket or a regime
- **THEN** the report SHALL declare the sample insufficient for that bucket or regime
- **AND** SHALL NOT present a conclusion about the threshold or the geometry from that sample

#### Scenario: No threshold change happens without the report

- **WHEN** a change of the confidence policy or of the barrier geometry is proposed
- **THEN** the report from this requirement SHALL exist for the sample in question
- **AND** without it the consumed confidence policy, `EXIT_TARGET_BP`, `EXIT_STOP_BP` and `HOLD_AFTER_FILL_S` SHALL stay unchanged

#### Scenario: The instrument is read-only

- **WHEN** the ruler runs
- **THEN** it SHALL NOT write to product tables, to the trading path, to the scalp state, to an applied confidence version or to any database
- **AND** it SHALL NOT require the scalp loop to be running

#### Scenario: The report uses the configured regime boundary

- **WHEN** the CLI boundary is omitted and `SCALP_REGIME_BOUNDARY_BP` is configured
- **THEN** the same value SHALL be used to segment the report passed to `build_report`
- **AND** both regimes SHALL remain closed when that boundary is absent or invalid
