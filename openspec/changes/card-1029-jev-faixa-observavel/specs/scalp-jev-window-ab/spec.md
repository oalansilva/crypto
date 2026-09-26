## ADDED Requirements

### Requirement: The larger state window is produced by the product configuration

The product SHALL produce the larger state window by configuration instead of only labelling it. The same configuration SHALL set the **retention** of the state window fed to the aggregates and the **horizon of the window aggregates** sent to the model, and the payload SHALL declare the effective window. The effective state window of the `current` arm SHALL stay 900 s; the larger window SHALL be strictly greater than 900 s.

#### Scenario: The larger window is actually sent

- **WHEN** the larger state window is selected
- **THEN** the trades and spreads retained SHALL cover the larger window
- **AND** the horizon of the window aggregates in the payload SHALL be the larger value
- **AND** the payload the model receives SHALL be built from the larger window

#### Scenario: The current window stays the current window

- **WHEN** the current state window is selected
- **THEN** the payload SHALL be built from the 900 s window
- **AND** the declared horizon SHALL be 900 s

#### Scenario: The declared horizon matches the effective window

- **WHEN** a payload is built
- **THEN** the horizon declared with the window aggregates SHALL equal the effective state window
- **AND** the model SHALL NOT receive the current window labelled as the larger one

### Requirement: The arm label is derived from the effective state window

The recorded A/B arm SHALL be derived from the effective state window actually sent. The product SHALL NOT let an independent setting label a record with the larger arm while the 900 s window was sent. A record with the larger arm SHALL imply that the larger window was sent, and a call that sends the larger window SHALL be recorded with the larger arm.

#### Scenario: The current window cannot be labelled larger

- **WHEN** the effective state window is 900 s
- **THEN** the record SHALL carry the current arm
- **AND** it SHALL NOT carry the larger arm, even if the larger arm was requested

#### Scenario: The larger window is labelled larger

- **WHEN** the effective state window is larger than 900 s
- **THEN** the record SHALL carry the larger arm

#### Scenario: The label follows the effective window

- **WHEN** the recorded arm is read together with the effective window
- **THEN** the larger arm SHALL hold if and only if the effective window is larger than 900 s
- **AND** the effective window SHALL be declared with the record

### Requirement: The A/B measures the mean confidence with the current window and with the larger window

The A/B SHALL record the **mean confidence with the current state window** and the **mean confidence with the larger state window**, SHALL use the **same fixed model version** (the pinned version delivered by the prerequisite of this card) in both arms, and SHALL declare the **sample size**. The budget of the input per call (≤ ~500 tokens, card #1025) SHALL be preserved in both arms.

#### Scenario: Both arms are recorded

- **WHEN** the A/B runs over the diagnostic records
- **THEN** it SHALL produce the mean confidence of the current window
- **AND** the mean confidence of the larger window

#### Scenario: Same fixed model version

- **WHEN** the A/B reads the sample
- **THEN** every record used SHALL carry the same fixed model version
- **AND** the version SHALL be declared with the result

#### Scenario: Sample size declared

- **WHEN** the A/B reports
- **THEN** it SHALL declare the number of windows used
- **AND** it SHALL declare the observations used per arm

#### Scenario: The payload budget is declared

- **WHEN** the payload is built with the larger state window
- **THEN** the input per call SHALL stay within the ≤ ~500-token budget
- **AND** the window block SHALL keep a fixed shape (the scalar aggregates plus at most the last N trades), so the larger window changes values and not the number of fields

### Requirement: The A/B only concludes with 30 non-overlapping 900 s windows

The A/B SHALL only conclude with at least **30 non-overlapping 900 s windows per arm**. Below that it SHALL NOT conclude, and the record SHALL write **amostra insuficiente**.

#### Scenario: Enough windows

- **WHEN** each arm has 30 or more non-overlapping 900 s windows
- **THEN** the A/B SHALL conclude with the mean confidence of both arms
- **AND** the conclusion SHALL declare the sample size

#### Scenario: Not enough windows

- **WHEN** any arm has fewer than 30 non-overlapping 900 s windows
- **THEN** the A/B SHALL NOT conclude
- **AND** the record SHALL write `amostra insuficiente`

#### Scenario: Overlapping observations are not counted twice

- **WHEN** two observations fall inside the same 900 s window
- **THEN** they SHALL count as one window
- **AND** only non-overlapping windows SHALL count towards the 30

### Requirement: The A/B analysis is read-only; the trial configuration differs by design but the gates and the question do not

The A/B **analysis** SHALL be read-only over the diagnostic records and SHALL NOT change the entry decision, the gates, the threshold, the question asked to the model or any product surface, and SHALL NOT add a Monitor panel, a route, HTML, a database table or an export. The **operational configuration of the trial** differs by design and SHALL only change the **state window (context)** sent to the model. The gates, the confidence threshold and the question (the ten options, `type: score`) SHALL be identical in both arms.

#### Scenario: The decision is untouched

- **WHEN** the A/B analysis is available
- **THEN** the entry decision for the same input SHALL be the same
- **AND** no gate, threshold or question SHALL be altered by the analysis

#### Scenario: The arms share the same gates, threshold and question

- **WHEN** the two arms are compared
- **THEN** the gates, the confidence threshold and the question SHALL be identical in both arms
- **AND** only the state window (context) sent to the model SHALL differ, by design

#### Scenario: No product surface gains the A/B

- **WHEN** the A/B is active
- **THEN** the Monitor panel, `/api/scalp/status`, any route or HTML and the database SHALL be unchanged
