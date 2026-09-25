## ADDED Requirements

### Requirement: The ruler reports accuracy and net return per confidence band with its sample size

The read-only Jev ruler (`scripts/scalp_jev_eval.py`) SHALL report, for each confidence band (width 0,1, as today) and for each **market regime**, the **sample size** (`n` and `n with price`), the **accuracy** (fraction of priced cycles whose realized signed return at the 900 s horizon is positive) and the **net return** in bp of each band. Accuracy SHALL be reported only: it SHALL NOT be the criterion that selects a threshold. A band whose priced sample is below the ruler's minimum SHALL be declared as insufficient instead of being concluded.

#### Scenario: Every confidence band carries accuracy, net return and sample size

- **WHEN** the ruler builds the report over a priced sample
- **THEN** each confidence band SHALL show its sample size, its accuracy and its net return in bp
- **AND** the net return SHALL subtract the round-trip cost (`2 × maker fee per leg`)

#### Scenario: A band below the minimum sample is declared

- **WHEN** a confidence band has fewer priced cycles than the ruler's minimum
- **THEN** the report SHALL mark that band as insufficient
- **AND** that band SHALL NOT justify a threshold

### Requirement: The ruler evaluates a threshold by coverage and expected net return

The ruler SHALL evaluate a candidate confidence threshold over the **eligible population** of a regime (the reply cycles that pass `hold`, `jev_late`, `hurdle`, `regime` and `toxic_book`, with a realized outcome) and SHALL report, for a candidate threshold: how many eligible cycles it lets pass, the **coverage** (passing cycles over the eligible population) and the **expected net return** of those cycles, where expected net return is `expected gain × coverage` and the expected gain is the mean net return of the passing cycles. The threshold of a regime SHALL be the candidate with the highest expected net return among those with sufficient sample, and the report SHALL show that chosen threshold with its coverage and its expected net return.

#### Scenario: A candidate threshold shows how many cycles it lets pass and their expected net return

- **WHEN** the ruler evaluates a candidate threshold over the eligible population of a regime
- **THEN** the report SHALL show the number of cycles that pass, the coverage and the expected net return of those cycles
- **AND** the expected net return SHALL be the expected gain multiplied by the coverage

#### Scenario: The chosen threshold is the one with the highest expected net return

- **WHEN** several candidate thresholds have sufficient sample in a regime
- **THEN** the reported threshold of that regime SHALL be the candidate with the highest expected net return
- **AND** the report SHALL show the chosen threshold's coverage and expected net return

### Requirement: The ruler reports one threshold per regime and declares a closed regime

The ruler SHALL segment the sample by the **market regime** defined on the window volatility (σ, `vol_bp`) against the **single configured regime boundary** shared with the decision, and SHALL report, for **each** regime (calm and active), the confidence band that justifies that regime's threshold and that regime's sample size. A regime whose eligible population with price is below the ruler's minimum, or that has no contributing band with the minimum sample, SHALL appear as **closed**.

#### Scenario: Each regime shows the band that justifies its threshold

- **WHEN** the report is built with a sufficient eligible population in a regime
- **THEN** that regime SHALL show the confidence band that justifies its threshold and its sample size
- **AND** the regime SHALL be reported as open with a justified threshold (or as not separating, per the separation requirement)

#### Scenario: A regime without a sufficient sample appears as closed

- **WHEN** a regime's eligible population with price is below the ruler's minimum, or no contributing band reaches the minimum sample
- **THEN** that regime SHALL appear as **closed** in the report
- **AND** no threshold SHALL be proposed for it

### Requirement: The ruler declares whether the confidence separates good from bad cycles

The ruler SHALL declare, per regime, whether the confidence **separates** good from bad cycles in this sample, where the confidence separates if and only if there is a threshold whose expected net return is strictly positive and strictly better than accepting every eligible cycle (threshold 0), with sufficient sample. When the confidence does not separate, the report SHALL say so explicitly and SHALL record the threshold as **turned off**.

#### Scenario: The confidence separates

- **WHEN** a threshold has a strictly positive expected net return and a strictly higher expected net return than accepting every eligible cycle
- **THEN** the report SHALL declare that the confidence separates in that regime
- **AND** the justified threshold SHALL be the one with the highest expected net return

#### Scenario: The confidence does not separate

- **WHEN** no threshold beats accepting every eligible cycle, or none has a strictly positive expected net return, with sufficient sample
- **THEN** the report SHALL declare explicitly that the confidence does not separate good from bad cycles in that regime
- **AND** the report SHALL record the threshold as turned off for that regime

### Requirement: The ruler declares insufficiency instead of concluding a threshold

The ruler SHALL propose no threshold and no numeric value while the sample is insufficient; it SHALL declare the insufficiency (globally and per regime) as such, never conclude it. With an insufficient sample the value in use SHALL be reported as preserved and no new numeric value SHALL be derived from the insufficient sample.

#### Scenario: Insufficient sample proposes nothing

- **WHEN** the non-overlapping windows with price, or a regime's eligible population, are below the ruler's minimum
- **THEN** the report SHALL declare the sample insufficient
- **AND** no confidence threshold SHALL be proposed
- **AND** the value in use SHALL be reported as preserved

### Requirement: The ruler uses the real per-leg fee of the account and records it

The cost used by the ruler SHALL be the round-trip of the **real maker fee per leg of the account in use** (the same value the decision consumes), and the report SHALL record the fee used and its source (account or the conservative fallback). Using the conservative fallback while the real fee is known SHALL be declared as a defect of the report, not treated as a neutral number.

#### Scenario: The real per-leg fee is recorded with its source

- **WHEN** the report computes the net return
- **THEN** the cost SHALL be `2 × maker fee per leg` and the report SHALL record the fee used and its source
- **AND** the fallback fee SHALL only be acceptable as a declared fallback

### Requirement: The ruler declares the homogeneity of the sample

The ruler SHALL declare the **model version** and the **confidence origin** of the sample (from the per-cycle record) and the number of windows excluded for a mixed origin or version. Without a homogeneous sample the ruler SHALL NOT propose a threshold.

#### Scenario: A mixed sample blocks the threshold

- **WHEN** the sample mixes confidence origins or model versions
- **THEN** the report SHALL declare the mixture and the excluded windows
- **AND** no threshold SHALL be proposed for that regime

#### Scenario: A homogeneous sample is declared

- **WHEN** the sample has a single model version and a single confidence origin with sufficient size
- **THEN** the report SHALL declare that version and origin as the sample's
- **AND** a threshold may be proposed from it

### Requirement: The ruler stays read-only

The ruler SHALL NOT write product tables, trading state or any database, and SHALL NOT need the scalp loop to run. It SHALL read the diagnostic log and the already stored OHLCV only, and it SHALL receive the fee per leg and the regime boundary as inputs instead of contacting the exchange.

#### Scenario: No write and no scalp loop

- **WHEN** the ruler runs over the diagnostic log and the stored OHLCV
- **THEN** it SHALL write nothing to product, trading state or the database
- **AND** it SHALL NOT require the scalp loop
- **AND** it SHALL NOT authenticate against the exchange
