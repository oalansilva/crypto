## ADDED Requirements

### Requirement: A cycle enters only when the forecast covers the maker cost with 50% slack

`decide_cycle` SHALL refuse the entry with the token `skip_reason="regime"` when the forecast does not cover the cost with the 50% slack over the maker cost — that is, unless `expected_move_bp >= entry_hurdle_bp × 1,5`, where `entry_hurdle_bp` uses the real maker fee. The `regime` gate SHALL be evaluated after the `hurdle` gate (which keeps its meaning of "does not cover the cost at all") and before the `toxic_book` gate, so that `hurdle` means "below cost" and `regime` means "at or above cost but without the 50% slack". In the calm regime no entry SHALL occur; in the active regime entries SHALL be allowed. The **primary input** of this gate SHALL be the forecast (`expected_move_bp`); σ (`vol_bp`) SHALL NOT be read as an interchangeable alternative — it MAY join only as a secondary or fallback condition, and only if the ruler's report justifies it. Until such a report exists, the gate SHALL decide on the forecast alone. The gate SHALL NOT be switchable off by configuration.

#### Scenario: Calm regime produces no entry with a visible regime skip

- **WHEN** the forecast in a calm regime does not reach `entry_hurdle_bp × 1,5`
- **THEN** the cycle SHALL be refused with `skip_reason="regime"`
- **AND** no order SHALL be sent

#### Scenario: Active regime allows entries

- **WHEN** the forecast covers the maker cost with the 50% slack
- **THEN** the `regime` gate SHALL NOT refuse the cycle
- **AND** the remaining gates SHALL be evaluated exactly as today

#### Scenario: The forecast is the primary input, not sigma

- **WHEN** the ruler's report has not justified σ (`vol_bp`) as an additional condition of the gate
- **THEN** the `regime` gate SHALL decide on the forecast (`expected_move_bp`) alone
- **AND** the clause "the forecast (or the horizon σ)" SHALL NOT be read as a free choice between the two

#### Scenario: Below cost is hurdle, above cost without slack is regime

- **WHEN** the forecast does not clear the bare `entry_hurdle_bp`
- **THEN** the refusal token SHALL be `hurdle`
- **WHEN** the forecast clears the bare hurdle but not `entry_hurdle_bp × 1,5`
- **THEN** the refusal token SHALL be `regime`

#### Scenario: The gate is not configurable off

- **WHEN** the scalp runs in any environment
- **THEN** the `regime` gate SHALL be active
- **AND** no environment flag SHALL disable it

### Requirement: Target and stop are recalibrated from the ruler; the 15-minute waiting window is a fixed product value

`EXIT_TARGET_BP` and `EXIT_STOP_BP` SHALL be recalibrated to a risk/reward coherent with the forecast and the maker cost, with the values taken from the ruler's report and justified by net expectancy and by the barrier break-even evidence. The **waiting window** (`HOLD_AFTER_FILL_S`, 15 minutes after the fill — the trigger of the aggressive exit) SHALL NOT be part of that recalibration: it is a product value fixed by the 23/09 grid, so that a window returned by the report cannot change the 15 minutes silently. Changing the 15 minutes SHALL be an explicit amendment of that decision, never an implicit consequence of the recalibration. The recalibration SHALL NOT be performed without the report; when the report is missing or inconclusive the current target and stop SHALL stay and the reason SHALL be recorded in the evidence.

#### Scenario: Geometry follows the ruler

- **WHEN** the ruler's report establishes the barrier break-even and the net expectancy per geometry
- **THEN** `EXIT_TARGET_BP` and `EXIT_STOP_BP` SHALL be set from that report
- **AND** the waiting window (`HOLD_AFTER_FILL_S`) SHALL stay at the 15-minute product value unless the 23/09 decision is explicitly amended
- **AND** the delivery evidence SHALL show the break-even and the expectancy the choice is based on

#### Scenario: No geometry change without the ruler

- **WHEN** the ruler's report is missing or inconclusive for the barrier geometry
- **THEN** the current `EXIT_TARGET_BP = 35 bp` and `EXIT_STOP_BP = −28 bp` SHALL stay unchanged
- **AND** the waiting window SHALL stay at 15 minutes
- **AND** the reason SHALL be recorded in the delivery evidence

#### Scenario: The waiting window does not move implicitly

- **WHEN** the ruler's report suggests a waiting window different from 15 minutes
- **THEN** the window SHALL NOT change as an implicit consequence of the recalibration
- **AND** either it stays at 15 minutes, or the change is recorded as an explicit amendment of the 23/09 decision

#### Scenario: Geometry stays coherent with the entry rule

- **WHEN** the geometry is recalibrated
- **THEN** the target SHALL be coherent with the forecast band the regime gate admits
- **AND** the barrier set SHALL NOT be left with a break-even incompatible with the maker cost in use
