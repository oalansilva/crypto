## ADDED Requirements

### Requirement: The diagnosis runs once per closed day

The system SHALL run the read-only Jev ruler once for each closed UTC calendar day, after 00:15 UTC, using only windows that have already ended by 00:00 UTC that day. It SHALL NOT create another diagnosis the same day because fifteen minutes passed or because the operator opened `/monitor`. The persisted diagnosis SHALL record the date, the evaluated period, the #1043 measurement state and the result. A second run for the same closed day SHALL return the diagnosis already stored and SHALL NOT apply the same adjustment again. The operator SHALL NOT need a terminal command for this daily run.

#### Scenario: One diagnosis after the day is closed

- **WHEN** the UTC day has closed and the daily run executes
- **THEN** the system SHALL store one diagnosis for that closed day
- **AND** SHALL include only windows that had already ended
- **AND** SHALL NOT store a further diagnosis later that same day

#### Scenario: Repeating the run does not apply twice

- **WHEN** the daily run for a closed day executes again
- **THEN** the stored diagnosis SHALL be the same one
- **AND** the same adjustment SHALL NOT be applied a second time

### Requirement: Quality gates block promotion without pretending the sample lost money

Before any confidence change the apply step SHALL consume the #1043 measurement state and the homogeneity, cost, benchmark and viability gates. A read failure, stale data (the newest stored candle is older than the last window end), inadequate coverage, an unverified sample, a cost that is not the account rate returned by the commission query, or a benchmark that cannot be computed SHALL block promotion. The account rate used for the hurdle SHALL be conservative across maker BUY/SELL and standard, tax and special commission components; it SHALL NOT subtract the BNB factor unless sufficient BNB for the fee is confirmed. The reason SHALL be explicit and SHALL NOT be presented as negative performance. When no candidate geometry or horizon beats its break-even, the diagnosis SHALL say não operável and SHALL NOT adopt any parameter. The posterior SHALL contain at least 200 independent, non-overlapping windows with realized prices that pass every non-confidence entry gate, measured apart from the sample that chose the adjustment. Missing, indeterminate, or ineligible windows SHALL NOT count toward 200. These are historical evaluation windows, not trades executed by the scalp. The diagnosis SHALL show the actual evaluated period and distinguish its windows from executed trades. The count of 300 SHALL NOT be an additional gate above 200.

#### Scenario: A short posterior sample does not move confidence

- **WHEN** fewer than 200 independent posterior windows with realized prices pass the non-confidence entry gates
- **THEN** the diagnosis SHALL appear with the date and the reason
- **AND** the consumed confidence policy SHALL stay unchanged

#### Scenario: A failed measurement is not a loss

- **WHEN** the #1043 state is `não medido` or the data is stale
- **THEN** promotion SHALL be blocked
- **AND** the reason SHALL NOT be presented as negative performance
- **AND** kill, the per-user switch and the other gates SHALL stay as they were

#### Scenario: Nothing is adopted when no geometry pays

- **WHEN** no candidate geometry or horizon beats its break-even with cost
- **THEN** the diagnosis SHALL declare the strategy não operável
- **AND** no parameter, including confidence, SHALL be adopted

### Requirement: Validated apply writes only the declared confidence outcome

The apply step SHALL be separate from the read-only ruler. On the first version it SHALL automatically apply only the per-regime confidence policy already defined for #1030: the numeric value the evaluation declares, the filter turned off, the regime stopped, or the regime reopened to the declared numeric-or-off outcome. It SHALL NOT clamp that value by an up or down step. It SHALL NOT change target, stop, horizon or size. For a change between policies that can be compared on the posterior sample, it SHALL swap only when the declared policy loses less than the current one on later data that was not used to choose it, after cost, even if the net result is still negative. If it does not lose less, the current policy SHALL stay and the reason SHALL be shown. Reopening a stopped regime SHALL NOT be required to beat zero: it SHALL apply only when at least 200 independent priced posterior windows pass every non-confidence entry gate, the posterior analysis declares the regime non-closed, and the chosen outcome is numeric or filter-off. A negative return SHALL NOT by itself keep a confirmed regime closed. If that posterior sample still closes the regime, the regime SHALL stay stopped and the reason SHALL be shown. The minimum interval in this design SHALL allow another confidence change on the next closed day when the new posterior sample excludes both the windows that chose the current version and the windows that validated it. It SHALL NOT change confidence twice on the same closed day. There SHALL NOT be a multi-day quarantine unless approval rejects this assumption.

#### Scenario: A still-negative improvement is applied

- **WHEN** calibration is enabled and the posterior sample has at least 200 independent priced windows that pass the non-confidence entry gates and were not used to choose the adjustment
- **AND** the declared policy's net result after cost is greater than the current policy's, while both are negative
- **THEN** the system SHALL apply that declared outcome with no step band
- **AND** SHALL NOT change target, stop, horizon or size

#### Scenario: No improvement keeps the current policy

- **WHEN** the declared policy does not lose less than the current one on the posterior sample
- **THEN** the consumed policy SHALL stay
- **AND** the operator SHALL see the reason

#### Scenario: Reopen does not have to beat zero

- **WHEN** the evaluation declares that a stopped regime reopens to a numeric value or a turned-off filter
- **AND** the posterior sample of at least 200 independent priced windows that pass the non-confidence entry gates confirms the regime is no longer closed
- **THEN** the system SHALL apply that declared outcome even if the net result is still negative

#### Scenario: Missing prices do not count toward the posterior floor

- **WHEN** 200 raw non-overlapping windows include one or more windows without a realized price or that fail a non-confidence entry gate
- **THEN** those windows SHALL NOT count toward the minimum of 200
- **AND** the confidence policy SHALL stay unchanged until 200 priced, eligible posterior windows are available

#### Scenario: The same closed day does not change confidence twice

- **WHEN** a confidence version was already accepted for the closed day
- **THEN** a later run that day SHALL NOT accept a second confidence change

### Requirement: The applied version is what the next entry consumes

The system SHALL record the previous value, the new value, the evidence, the reason and the applied version. The version shown to the operator SHALL be the active version and policy the scalper consumes on its next entry, including after a manual revert. As soon as the swap is accepted, the next entry SHALL use the new confidence. A position that was already open SHALL exit as it was, without retargeting from the new confidence. The operator SHALL NOT have to turn the scalp switch off. Repeating an execution SHALL NOT apply the same adjustment twice. Automatic reversal, under the design assumption, SHALL on a later closed day restore the immediately previous version when a fresh sample of at least 200 independent priced windows that pass the non-confidence entry gates, not used to validate the swap, shows that the applied version loses more after cost than that previous version. The restored fingerprint SHALL retain the inclusive validation cutoff that rejected it, so those windows cannot be reused in a later validation. A manual revert SHALL also advance the restored fingerprint's cutoff through evidence already used by the version being reverted. The system SHALL NOT invent a third number, SHALL NOT revert on the same day as the apply, and SHALL NOT revert because the measurement failed.

#### Scenario: The next entry uses the new confidence

- **WHEN** a confidence swap is accepted
- **THEN** the next entry and the scalp status SHALL use the new confidence and the new version
- **AND** an already open position SHALL exit under the target, stop and horizon already in force
- **AND** the per-user switch SHALL NOT be turned off by the swap

#### Scenario: Automatic revert restores the previous version

- **WHEN** a later closed day has a fresh sample of at least 200 independent priced windows that pass the non-confidence entry gates and did not validate the swap
- **AND** the applied version's net result after cost is worse than the immediately previous version on that sample
- **THEN** the system SHALL restore that previous version
- **AND** SHALL record the reason as reverter
- **AND** SHALL NOT invent a new confidence number

#### Scenario: Reversal does not reuse validation windows

- **WHEN** an automatic or manual revert reactivates a previously registered fingerprint
- **THEN** the restored version SHALL persist the latest inclusive validation cutoff already used
- **AND** a later posterior SHALL contain only priced windows after that cutoff

#### Scenario: A measurement failure does not revert

- **WHEN** the measurement for a later day fails or the sample is not verified
- **THEN** the applied version SHALL stay
- **AND** the diagnosis SHALL block promotion instead of reverting

### Requirement: The operator can pause calibration and revert from the system

Automatic calibration SHALL start paused. The operator SHALL be able to enable and pause it from the scalp module. While paused, the daily diagnosis SHALL still run and SHALL NOT apply. Enabling calibration SHALL NOT turn the scalper on and SHALL NOT send an order by itself. A diagnosis failure SHALL NOT weaken the existing switch, kill or other gates. The operator SHALL be able to revert to a previous registered version without waiting for 200 independent posterior windows. That manual revert SHALL take effect on the next entry, SHALL NOT retarget an open position, and SHALL NOT turn the switch off. The same day's automatic run SHALL NOT reapply the fingerprint the operator just reverted.

#### Scenario: Paused calibration still shows the diagnosis

- **WHEN** automatic calibration is paused and the closed day is diagnosed
- **THEN** the diagnosis SHALL appear
- **AND** the consumed confidence policy SHALL stay unchanged
- **AND** the scalp switch SHALL stay as the user left it

#### Scenario: Manual revert does not wait for the posterior sample

- **WHEN** the operator reverts to a previous registered version
- **THEN** the next entry SHALL consume that version
- **AND** the action SHALL be stored in the history
- **AND** an open position SHALL exit as it was
