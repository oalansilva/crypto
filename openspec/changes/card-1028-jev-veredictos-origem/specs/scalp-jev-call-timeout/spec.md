## ADDED Requirements

### Requirement: The model call timeout is 3 s with the 1.5 s late refusal unchanged

The timeout of the call to the model SHALL be **3 s**, decoupled from the late gate. The late gate SHALL keep refusing a reply whose latency is above **1.5 s** (`JEV_LATE_MS`) exactly as today. A reply that arrives between 1.5 s and 3 s SHALL therefore be received, mapped and recorded, and the cycle SHALL still be refused as late. The model-call timeout SHALL no longer be the same number as the late refusal.

#### Scenario: A reply between 1.5 s and 3 s is recorded and still refused

- **WHEN** the model replies after more than 1.5 s and within 3 s
- **THEN** the reply SHALL be recorded (return record and cycle record) with its real latency
- **AND** the cycle SHALL still be refused by the late gate (`jev_late`), exactly as today

#### Scenario: A reply within 1.5 s is untouched

- **WHEN** the model replies within 1.5 s
- **THEN** the call and the decision SHALL behave exactly as today

#### Scenario: No reply within the timeout

- **WHEN** the model does not reply within 3 s
- **THEN** the call SHALL close with the transport/error record and the cycle SHALL be refused as late, exactly as today

### Requirement: The timeout change does not change any decision

Raising the call timeout to 3 s SHALL NOT change the decision: for the same input, the resulting decision (`send` or the first `skip_reason`) SHALL be the same as before this change. A slow reply that today closed as a transport error and was refused as late SHALL keep being refused as late after the change.

#### Scenario: Slow reply keeps the same decision

- **WHEN** the same slow reply (latency above 1.5 s) is processed before and after the timeout change
- **THEN** the decision SHALL be the same in both cases (refused by the late gate, no order sent)
- **AND** only the record SHALL differ (a recorded reply instead of a lost one)

#### Scenario: The late gate constant is unchanged

- **WHEN** the timeout is set to 3 s
- **THEN** the late refusal threshold SHALL remain 1.5 s
- **AND** the other gates, the cadence, the freshness fail-closed, the target and the stop SHALL remain unchanged
