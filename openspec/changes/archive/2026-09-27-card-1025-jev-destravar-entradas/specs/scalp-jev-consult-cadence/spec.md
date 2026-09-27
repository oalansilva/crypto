## ADDED Requirements

### Requirement: The Jev consult cadence is configurable and defaults to 30 seconds

`JEV_TARGET_MS` SHALL be read from environment configuration with a default of **30 s** (30000 ms), replacing the current hard-coded 1 s. The configured value SHALL drive the `jev_target` gate and the post-call cadence input, while the pure `scalp_engine` module SHALL keep receiving it as a parameter instead of reading the environment itself. The cycle loop interval SHALL stay as it is (it paces the same cycle that handles the resting order sync, the exit target/stop and the stuck mark), so the consult rate SHALL fall by at least 15× relative to 1 Hz. The `JEV_LATE_MS` fail-closed and every other gate SHALL stay unchanged.

#### Scenario: Cadence defaults to 30 seconds

- **WHEN** the scalp runs without an explicit cadence configuration
- **THEN** consecutive Jev consults for the same user SHALL be spaced by 30 s
- **AND** the requests per hour SHALL be at least 15× lower than at 1 Hz

#### Scenario: Cadence is configurable

- **WHEN** the operator sets the cadence by environment configuration
- **THEN** the `jev_target` gate SHALL use that value
- **AND** the pure engine SHALL receive it as a parameter, not read the environment

#### Scenario: The cycle loop keeps its pace

- **WHEN** the cadence is set to 30 s
- **THEN** the resting-order sync, the exit target/stop evaluation and the stuck mark SHALL keep running at the loop's own interval
- **AND** an exit decision SHALL NOT wait for the next Jev consult

#### Scenario: Fail-closed stays as it is

- **WHEN** the cadence changes
- **THEN** the 1.5 s `JEV_LATE_MS` fail-closed and the other gates SHALL keep their current values
- **AND** a late reply SHALL still be refused with `jev_late`

### Requirement: The payload sent to Jev is summarized and stays within about 500 tokens per call

The window transported to the Jev SHALL be summarized: aggregates of the 900 s horizon plus the last N trades, never a full tick dump. The fixed question block SHALL be compacted so that the input per call stays at most about 500 tokens (today 1158). The ladder `score → bp` SHALL NOT change: its ten levels `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` and their meaning SHALL be preserved.

#### Scenario: Input per call stays within the budget

- **WHEN** a Jev call is assembled and sent
- **THEN** the input SHALL stay at most about 500 tokens
- **AND** the measurement SHALL be part of the delivery evidence

#### Scenario: Window is aggregates plus recent trades

- **WHEN** the payload is built
- **THEN** the window SHALL carry the 900 s horizon aggregates and at most the last N trades
- **AND** SHALL NOT carry the full tick dump

#### Scenario: Ladder is untouched

- **WHEN** the question block is compacted
- **THEN** the `score → bp` ladder SHALL keep its ten levels `(0, 5, 10, 15, 20, 25, 30, 35, 50, 80)` and their meaning
- **AND** the ladder values SHALL NOT be reduced or re-scaled

### Requirement: The measured latency no longer includes the entry registration

The `latency_ms` that feeds the fail-closed `jev_late` gate SHALL be measured from after the diagnostic entry registration, so that writing the entry record does not inflate the latency. The entry record SHALL still be written as delivered by #1015.

#### Scenario: Latency measures the call, not the registration

- **WHEN** a Jev call completes and the entry record has been written
- **THEN** the recorded `latency_ms` SHALL measure the call itself
- **AND** SHALL NOT include the time spent writing the entry record

#### Scenario: The entry record is still written

- **WHEN** the latency measurement starts after the entry registration
- **THEN** the diagnostic log SHALL still contain the entry record
- **AND** the #1015 record set SHALL stay intact

#### Scenario: The late gate does not trip on the registration

- **WHEN** a prompt reply arrives whose call time is within `JEV_LATE_MS`
- **THEN** the cycle SHALL NOT be refused with `jev_late` because of the entry registration cost
