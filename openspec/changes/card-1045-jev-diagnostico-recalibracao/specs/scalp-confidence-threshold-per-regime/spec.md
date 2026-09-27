## MODIFIED Requirements

### Requirement: A closed regime does not operate and preserves the value in use

A **closed** regime SHALL NOT operate: its cycles SHALL close without an order with the closed-regime token, and the closure SHALL be visible in the diagnostic record together with the market regime and the confidence verdict. An insufficient or unverified report SHALL NOT rewrite the policy the scalper is already consuming. While no applied version exists, an insufficient sample SHALL leave the regime closed and SHALL preserve the configured value in use. A previously applied version SHALL stay in force until the separate apply step of `scalp-jev-diagnostico-recalibracao` accepts another version or a revert. Only that step, and only after a sufficient report, SHALL open a regime with a justified numeric threshold or turn the filter off.

#### Scenario: Insufficient sample keeps the bot from operating

- **WHEN** no applied version exists and the ruler declares the sample insufficient for a regime
- **THEN** that regime's policy SHALL be closed and no order SHALL be sent in it
- **AND** the value in use SHALL be preserved and reported
- **AND** no numeric threshold SHALL be adopted without a sufficient report

#### Scenario: An insufficient rerun does not rewrite an applied version

- **WHEN** an applied confidence version is what the scalper consumes
- **AND** a later report declares the sample insufficient or não verificada
- **THEN** the consumed policy SHALL stay that applied version
- **AND** the report SHALL NOT be presented as negative performance

#### Scenario: The closed refusal is visible in the log

- **WHEN** a cycle is closed because its regime is closed
- **THEN** the diagnostic record SHALL carry the closed-regime token, the market regime and the confidence verdict in the same record
- **AND** the token SHALL NOT be `regime` nor `low_confidence`

### Requirement: The confidence configuration is explicit and reversible

The confidence policy per regime SHALL stay explicit and reversible. Each regime SHALL accept a numeric value in [0, 1], a turned-off token or a closed token. A missing, non-finite or out-of-range value SHALL fall back to **closed** (fail closed). No numeric value SHALL be adopted without a sufficient ruler report and the separate validated apply step. When an applied version exists, the value in use SHALL be that version, not a divergent environment variable. Reverting the applied version SHALL restore the previous registered policy. The three policy kinds SHALL keep the meaning they have in this specification.

#### Scenario: The applied version is the value in use

- **WHEN** an applied version exists for a regime
- **THEN** the threshold or token consumed on the next entry SHALL be the one in that version
- **AND** the status payload SHALL report that same version

#### Scenario: Configuration sets the policy per regime

- **WHEN** no applied version exists and a regime's configuration carries a numeric value in [0, 1]
- **THEN** that value SHALL be the threshold applied in that regime
- **AND** reverting the value in configuration SHALL revert the policy

#### Scenario: An invalid value fails closed

- **WHEN** a regime's configuration is missing or carries a non-finite or out-of-range value, and no applied version exists
- **THEN** the regime SHALL be closed
- **AND** no order SHALL be sent in it

## REMOVED Requirements

### Requirement: The threshold change is log-only and leaves the other gates untouched
**Reason**: Card #1045 requires the diagnosis, the applied confidence version and the reason to be visible on `/monitor` and persisted in the existing database. The log-only ban on the Monitor, on `/api/scalp/status` and on persistence contradicts that scope.
**Migration**: Refusals remain in the diagnostic log. The other reply-fed gates stay as specified in the added requirement below. Presentation and persistence of the applied version belong to `scalp-jev-diagnostico-recalibracao`.

## ADDED Requirements

### Requirement: The other gates stay untouched when the confidence policy changes

Changing or displaying the per-regime confidence policy SHALL NOT change the other reply-fed gates (`hurdle`, the cost-with-slack `regime` gate, `toxic_book`), the barrier geometry in force, the hold window or the aggressive exit. Refusals SHALL still be written to the existing diagnostic log. The Monitor SHALL be allowed to show the diagnosis and the applied version only as specified by `scalp-jev-diagnostico-recalibracao`.

#### Scenario: The other gates are unchanged

- **WHEN** the same reply is evaluated after a confidence version is applied
- **THEN** the `hurdle`, cost-with-slack `regime` and `toxic_book` verdicts SHALL be the same as before the confidence change
- **AND** target, stop, horizon and size SHALL stay unchanged
