## ADDED Requirements

### Requirement: The A/B measures the mean confidence with the current window and with the larger window

The A/B SHALL record the **mean confidence with the current state window** and the **mean confidence with the larger state window**, SHALL use the **same fixed model version** (the pinned version delivered by the prerequisite of this card) in both arms, and SHALL declare the **sample size**.

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

### Requirement: The A/B only concludes with 30 non-overlapping 900 s windows

The A/B SHALL only conclude with at least **30 non-overlapping 900 s windows**. Below that it SHALL NOT conclude, and the record SHALL write **amostra insuficiente**.

#### Scenario: Enough windows

- **WHEN** the sample has 30 or more non-overlapping 900 s windows
- **THEN** the A/B SHALL conclude with the mean confidence of both arms
- **AND** the conclusion SHALL declare the sample size

#### Scenario: Not enough windows

- **WHEN** the sample has fewer than 30 non-overlapping 900 s windows
- **THEN** the A/B SHALL NOT conclude
- **AND** the record SHALL write `amostra insuficiente`

#### Scenario: Overlapping observations are not counted twice

- **WHEN** two observations fall inside the same 900 s window
- **THEN** they SHALL count as one window
- **AND** only non-overlapping windows SHALL count towards the 30

### Requirement: The A/B is read-only and does not change the decision

The A/B SHALL be a read-only analysis over the diagnostic records. It SHALL NOT change the entry decision, the gates, the question asked to the model or any product surface, and it SHALL NOT add a Monitor panel, a route, HTML, a database table or an export.

#### Scenario: The decision is untouched

- **WHEN** the A/B analysis is available
- **THEN** the entry decision for the same input SHALL be the same
- **AND** no gate, threshold or question SHALL be altered

#### Scenario: No product surface gains the A/B

- **WHEN** the A/B is active
- **THEN** the Monitor panel, `/api/scalp/status`, any route or HTML and the database SHALL be unchanged
