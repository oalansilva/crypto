## ADDED Requirements

### Requirement: The raw Jev reply payload can be logged opt-in without secrets

The Farol SHALL be able to record the **raw** reply payload of the Jev call when enabled by environment configuration (opt-in), in the #1015 diagnostic log, so that the origin of `confidence` can be established — `side_answer.confidence` versus `probabilities[choice]` — together with the raw `expected_move_bp` score and the `noul` value. The record SHALL NOT contain any secret (no Jev/TypeSafe key, no token, no `Authorization` header) and SHALL NOT contain exact balance or position values. With the opt-in disabled, the records of the #1015 log SHALL stay exactly as they are.

#### Scenario: Opt-in record shows the origin of confidence

- **WHEN** the raw-payload record is enabled and a Jev reply arrives
- **THEN** the log SHALL contain the raw answer fields that carry the confidence (`side_answer.confidence`, `probabilities[choice]`), the raw score and the `noul`
- **AND** the operator SHALL be able to tell whether `confidence` comes from a different field or scale than expected

#### Scenario: Opt-in disabled keeps today's records

- **WHEN** the raw-payload record is disabled
- **THEN** the diagnostic log SHALL contain only the #1015 records as they are today
- **AND** no raw reply payload SHALL be written

#### Scenario: No secret and no exact account value in the raw record

- **WHEN** a raw-payload record is written
- **THEN** it SHALL contain no key, token or `Authorization` value
- **AND** it SHALL contain no exact balance or position value

### Requirement: The confidence gate is calibrated from the ruler, or removed

`CONFIDENCE_MIN` SHALL be configurable by environment configuration. Its value SHALL come from the ruler: the lowest bucket threshold whose net expectancy is positive, and never above the observed range of `confidence`. When the ruler shows that `confidence` does not separate good from bad trades, the confidence gate SHALL be removed — no threshold SHALL remain — and the entry decision SHALL become forecast × cost × regime. No confidence threshold SHALL be set without the ruler's report.

#### Scenario: Threshold comes from the ruler

- **WHEN** the ruler reports `confidence` buckets with net expectancy and one or more positive buckets exist
- **THEN** `CONFIDENCE_MIN` SHALL be set to the threshold of the lowest bucket with positive net expectancy
- **AND** SHALL NOT be set above the maximum `confidence` observed in the sample

#### Scenario: Gate falls when confidence does not separate

- **WHEN** the ruler shows that `confidence` does not separate good trades from bad trades
- **THEN** the confidence gate SHALL be removed from the cycle decision
- **AND** no `low_confidence` refusal SHALL be produced, the decision being forecast × cost × regime

#### Scenario: No bucket with negative expectancy passes the gate

- **WHEN** the calibrated threshold is applied to the ruler's buckets
- **THEN** no bucket with negative net expectancy SHALL pass the gate

#### Scenario: No threshold is invented without the ruler

- **WHEN** the ruler's report is missing or declares an insufficient sample for the confidence question
- **THEN** `CONFIDENCE_MIN` SHALL keep its current default value
- **AND** the reason SHALL be recorded in the delivery evidence
