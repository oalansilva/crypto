# scalp-confidence-gate Specification

## Purpose
TBD - created by syncing change card-1025-jev-destravar-entradas. Update Purpose after archive.
## Requirements

### Requirement: The raw Jev reply payload can be logged opt-in without secrets

The Farol SHALL be able to record the **raw** reply payload of the Jev call when enabled by environment configuration (opt-in), in the #1015 diagnostic log, so that the origin of `confidence` can be established — `side_answer.confidence` versus `probabilities[choice]` — together with the raw `expected_move_bp` score and the `noul` value. The record SHALL NOT contain any secret (no Jev/TypeSafe key, no token, no `Authorization` header) and SHALL NOT contain exact balance or position values. The opt-in covers **only** the raw-payload record: the #1015 return record keeps being written as always, including the always-on drivers of `book_toxic` required by the `scalp-book-toxic-observability` spec (`noul`, the window features and the resulting flag). With the opt-in disabled, no raw reply payload SHALL be written.

#### Scenario: Opt-in record shows the origin of confidence

- **WHEN** the raw-payload record is enabled and a Jev reply arrives
- **THEN** the log SHALL contain the raw answer fields that carry the confidence (`side_answer.confidence`, `probabilities[choice]`), the raw score and the `noul`
- **AND** the operator SHALL be able to tell whether `confidence` comes from a different field or scale than expected

#### Scenario: Opt-in disabled writes no raw payload while the return record stays

- **WHEN** the raw-payload record is disabled
- **THEN** no raw reply payload SHALL be written
- **AND** the #1015 return record SHALL keep being written with its fields, including the always-on `book_toxic` drivers of the `scalp-book-toxic-observability` spec

#### Scenario: No secret and no exact account value in the raw record

- **WHEN** a raw-payload record is written
- **THEN** it SHALL contain no key, token or `Authorization` value
- **AND** it SHALL contain no exact balance or position value

### Requirement: Confidence thresholds are ruler-derived and scoped per market regime

The confidence policy SHALL be per market regime as defined by `scalp-confidence-threshold-per-regime`. This later policy refines the single global calibration described by card #1025: numeric thresholds SHALL be selected per regime only when sufficient ruler evidence supports them; a regime SHALL be turned off when the ruler shows no separation and closed when the sample is insufficient. No numeric threshold SHALL be inferred from an insufficient report, and any justified threshold SHALL NOT exceed confidence observed in its regime. The global `CONFIDENCE_MIN` from the earlier contract SHALL NOT override a regime's configured `numeric`, `off` or `closed` policy.

#### Scenario: Threshold comes from the ruler

- **WHEN** the ruler reports sufficient confidence buckets for a regime and one or more candidate thresholds have positive net expectancy
- **THEN** that regime SHALL use its ruler-justified threshold under `scalp-confidence-threshold-per-regime`
- **AND** the threshold SHALL NOT exceed the maximum `confidence` observed in that regime

#### Scenario: Gate falls when confidence does not separate

- **WHEN** the ruler shows that `confidence` does not separate good trades from bad trades in a regime
- **THEN** that regime's confidence policy SHALL be turned off
- **AND** no `low_confidence` refusal SHALL be produced in that regime

#### Scenario: No bucket with negative expectancy passes the gate

- **WHEN** a regime's calibrated numeric threshold is applied to the ruler's buckets
- **THEN** no bucket with negative net expectancy SHALL pass the gate

#### Scenario: No threshold is invented without the ruler

- **WHEN** the ruler's report is missing or declares an insufficient sample for a regime
- **THEN** that regime SHALL remain closed under `scalp-confidence-threshold-per-regime`
- **AND** no numeric value SHALL be adopted without a sufficient report


