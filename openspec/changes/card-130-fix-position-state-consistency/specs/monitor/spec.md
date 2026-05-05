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
