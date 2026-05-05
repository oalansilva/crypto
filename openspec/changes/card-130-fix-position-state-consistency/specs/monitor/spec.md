## MODIFIED Requirements

### Requirement: Monitor chart current marker matches active position state
The Monitor chart modal MUST represent an active `HOLD` opportunity as an open long position, not as an executed exit/sell marker.

#### Scenario: HOLD opportunity opens chart
- **WHEN** a Monitor opportunity is classified as active `HOLD`
- **AND** the chart has no historical signal markers to render
- **THEN** the chart current marker MUST use a long/entry-style visual
- **AND** the chart MUST NOT label the current marker as `EXIT`
- **AND** the distance panel MAY still label the next decision as `exit`

#### Scenario: WAIT or EXIT opportunity opens chart
- **WHEN** a Monitor opportunity is not an active `HOLD`
- **THEN** the chart marker and distance context MUST continue to follow the existing WAIT/EXIT resolution rules

#### Scenario: Current EXIT signal exists after the active entry
- **WHEN** the generated signal history has an `exit` event after the latest `entry`
- **THEN** the Monitor payload MUST classify the opportunity as not holding
- **AND** the Monitor list MUST place the opportunity in `EXIT`, not `HOLD`
- **AND** the chart modal MUST resolve the same opportunity as `EXIT` when the latest visible signal is the current exit execution candle
