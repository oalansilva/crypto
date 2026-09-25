## ADDED Requirements

### Requirement: The confidence gate applies a policy per market regime

The entry decision SHALL apply a **confidence policy per market regime**: a numeric threshold justified by the ruler's report, **turned off** (the gate is removed and the decision runs on forecast × cost × regime) or **closed** (the regime does not operate). The gate SHALL evaluate the policy of the regime the cycle belongs to. The pure engine SHALL receive the policy and the market regime as parameters and SHALL read no environment.

#### Scenario: A numeric policy keeps a confidence refusal

- **WHEN** a regime's policy is a numeric threshold and the reply confidence is below it
- **THEN** the cycle SHALL close with a `low_confidence` refusal, as today
- **AND** the threshold applied SHALL be that regime's value

#### Scenario: A turned-off policy produces no confidence refusal

- **WHEN** a regime's policy is turned off
- **THEN** the cycle SHALL NOT close with a `low_confidence` refusal
- **AND** the decision SHALL run on forecast × cost × regime

#### Scenario: A closed policy closes the cycle with its own token

- **WHEN** a regime's policy is closed
- **THEN** the cycle SHALL close without an order with a refusal token of its own, distinct from `regime` and from `low_confidence`
- **AND** no threshold comparison SHALL be required to close it

### Requirement: The market regime comes from the window volatility against a single configured boundary

The market regime SHALL be derived from the window volatility (σ, `vol_bp`) against the **single configured regime boundary** (calm below it, active at or above it), the same boundary the ruler uses. When the boundary is absent or invalid, both regimes SHALL be treated as **closed** (fail closed) instead of applying a threshold.

#### Scenario: The volatility decides the regime

- **WHEN** a cycle has a reply and the window volatility is below the configured boundary
- **THEN** the cycle SHALL belong to the calm regime
- **AND** the policy of the calm regime SHALL be the one applied

#### Scenario: No boundary closes both regimes

- **WHEN** the regime boundary is absent or invalid
- **THEN** both regimes SHALL be closed
- **AND** the cycle SHALL close without an order with the closed-regime token

### Requirement: A closed regime does not operate and preserves the value in use

A **closed** regime SHALL NOT operate: its cycles SHALL close without an order with the closed-regime token, and the closure SHALL be visible in the diagnostic record together with the market regime and the confidence verdict. While the ruler declares an insufficient sample, the policy SHALL stay closed and the configured value in use SHALL be preserved and reported — never rewritten by an insufficient report. Only a sufficient report SHALL open a regime with a justified numeric threshold.

#### Scenario: Insufficient sample keeps the bot from operating

- **WHEN** the ruler declares the sample insufficient for a regime
- **THEN** that regime's policy SHALL be closed and no order SHALL be sent in it
- **AND** the value in use SHALL be preserved and reported
- **AND** no numeric threshold SHALL be adopted without a sufficient report

#### Scenario: The closed refusal is visible in the log

- **WHEN** a cycle is closed because its regime is closed
- **THEN** the diagnostic record SHALL carry the closed-regime token, the market regime and the confidence verdict in the same record
- **AND** the token SHALL NOT be `regime` nor `low_confidence`

### Requirement: The confidence configuration is explicit and reversible

The confidence policy per regime SHALL be explicit and reversible by configuration: each regime SHALL accept a numeric value in [0, 1], a turned-off token or a closed token. A missing, non-finite or out-of-range value SHALL fall back to **closed** (fail closed). No numeric value SHALL be adopted without a sufficient ruler report.

#### Scenario: Configuration sets the policy per regime

- **WHEN** a regime's configuration carries a numeric value in [0, 1]
- **THEN** that value SHALL be the threshold applied in that regime
- **AND** reverting the value in configuration SHALL revert the policy

#### Scenario: An invalid value fails closed

- **WHEN** a regime's configuration is missing or carries a non-finite or out-of-range value
- **THEN** the regime SHALL be closed
- **AND** no order SHALL be sent in it

### Requirement: The threshold change is log-only and leaves the other gates untouched

The per-regime confidence policy SHALL write its refusals to the existing diagnostic log only. It SHALL NOT add or change anything in the Monitor panel, in `/api/scalp/status`, in any route or HTML, in the database or in any export/Drive surface. The other reply-fed gates (`hurdle`, the cost-with-slack `regime` gate, `toxic_book`), the barrier geometry, the hold window and the aggressive exit SHALL stay as delivered.

#### Scenario: No product surface gains the per-regime policy

- **WHEN** cycles are evaluated with the per-regime policy active
- **THEN** the Monitor panel and `/api/scalp/status` SHALL NOT gain the regime, the policy or the threshold
- **AND** no new route, HTML or database table SHALL be introduced

#### Scenario: The other gates are unchanged

- **WHEN** the same reply is evaluated with the per-regime policy active
- **THEN** the `hurdle`, cost-with-slack `regime` and `toxic_book` verdicts SHALL be the same as before this change
- **AND** only the confidence gate SHALL change its input
