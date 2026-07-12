## ADDED Requirements

### Requirement: Monitor ignores temporally invalid favorite trade events
The Monitor MUST use a cached favorite entry or exit as authoritative position evidence only when the event is temporally compatible with the candle coverage used by the analysis.

#### Scenario: Exit occurs after the latest available candle
- **WHEN** the latest cached trade contains an exit timestamp after the latest analysis candle
- **THEN** the system MUST ignore that exit when resolving the current position
- **AND** MUST NOT force `EXIT`, `Venda`, or a closed position from that event

#### Scenario: Active entry has no valid later exit
- **WHEN** a valid entry is covered by the analysis candles and no valid later exit exists
- **THEN** the Monitor MUST resolve the long position as `HOLD`/`Compra`

#### Scenario: Cached exit predates a newer calculated entry
- **WHEN** a cached exit is within the candle range but a newer entry is present in the current calculated signal history
- **THEN** the cached exit MUST NOT overwrite the newer active entry
- **AND** the Monitor MUST remain `HOLD`/`Compra`

#### Scenario: Confirmed exit is covered by candles
- **WHEN** a valid exit occurs after the active entry and within the analysis candle coverage
- **THEN** the Monitor MUST resolve the position as `EXIT`/`Venda`
- **AND** badge, message and position state MUST reference that same exit

### Requirement: Monitor chart markers follow the resolved position evidence
The Monitor chart MUST keep its visible markers consistent with the temporally valid position evidence returned for the opportunity.

#### Scenario: Invalid future exit exists in cached history
- **WHEN** cached history contains a future exit outside the displayed candle range
- **THEN** the chart MUST NOT render or synthesize a sale marker from that exit
- **AND** an active visible entry MUST remain represented as `Compra`

#### Scenario: Valid exit is visible
- **WHEN** the resolved opportunity is exited and the corresponding exit is covered by displayed candles
- **THEN** the chart MUST render `Venda` on the correct candle
- **AND** the card badge and chart marker MUST agree

### Requirement: Favorite refresh rejects future trade evidence
The favorite refresh process MUST NOT replace previously valid metrics with a result whose trade events extend beyond the returned analysis candle coverage.

#### Scenario: Refreshed result contains a future trade event
- **WHEN** a refresh result contains an entry or exit later than its latest returned candle
- **THEN** the refresh MUST fail or remove the invalid event before persistence according to execution semantics
- **AND** MUST NOT publish that event as current Monitor state

#### Scenario: Position remains open at end of deep-backtest period
- **WHEN** a deep backtest reaches the end of available candles without exit logic or stop being triggered
- **THEN** the system MUST NOT synthesize an exit on the following day
- **AND** MUST NOT record `end_of_period` as a realized `signal_15m` trade

#### Scenario: Real intraday stop closes the final position
- **WHEN** a stop is reached in covered intraday candles before the backtest period ends
- **THEN** the system MUST preserve the stop exit and its covered timestamp

### Requirement: Cached result history is safe on read
The system MUST validate saved favorite trades against their saved candle coverage before returning or rendering them, including caches created before this change.

#### Scenario: Legacy cache contains future exit
- **WHEN** saved metrics contain an exit outside the saved analysis candle coverage
- **THEN** the read model MUST remove the invalid exit while preserving its valid entry
- **AND** MUST expose the final operation as open rather than sold

#### Scenario: Results table receives open operation
- **WHEN** a trade has a valid entry and no valid exit
- **THEN** the results table MUST display the entry as an open position
- **AND** MUST NOT render a fabricated exit row, exit price or realized profit
