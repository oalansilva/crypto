## ADDED Requirements

### Requirement: The record always shows the chosen band and the position on the scale, never an interpolated bp

Every diagnostic record that carries the model's movement answer (the call return record and the cycle record) SHALL show the **band of the level already reached** and the **position on the scale**, and SHALL NEVER show a bp value derived by interpolating between levels of the scale. Any bp shown SHALL be the exact bp of a level of the scale.

#### Scenario: Record carries the band and the position

- **WHEN** a reply with a movement score is recorded
- **THEN** the record SHALL carry the band of the level already reached
- **AND** it SHALL carry the position on the scale (the reply's score / the level reached)

#### Scenario: No interpolated value anywhere in the record

- **WHEN** any diagnostic record is written
- **THEN** no field SHALL carry a bp value that is not a level of the scale
- **AND** the bp SHALL be reproducible from the position by reading the level, never by interpolating

#### Scenario: The quantization artifact is no longer produced

- **WHEN** a reply with a fractional score between two levels is recorded (for example 3.07, 2.86 or 0.92)
- **THEN** the record SHALL NOT produce the values 15,35 / 14,30 / 4,60 (the linear interpolation of those scores)
- **AND** the recorded bp SHALL be the exact bp of the level already reached (15 / 10 / 0)

### Requirement: Linear interpolation leaves the decision path

The conversion that interpolates linearly between levels of the scale SHALL leave the decision path. The decision and the record SHALL read the reply as a position and SHALL use only the exact bp of the level already reached.

#### Scenario: The interpolated value is not used

- **WHEN** the reply's score lies between two levels
- **THEN** the decision SHALL use the level already reached
- **AND** the linear interpolation SHALL NOT be in the path that produces the decision or the record

#### Scenario: The contract assertions stop fixing the interpolated value

- **WHEN** the tests that fixed the interpolated values are run
- **THEN** they SHALL assert the level already reached (for example score 4.5 credits level 4 = 20 bp, never 22.5 bp)

### Requirement: The record change is log-only

The band and the position SHALL go to the diagnostic log file only. They SHALL NOT add or change anything in the Monitor panel, in `/api/scalp/status`, in any route or HTML, in the database or in any export/Drive surface. The diagnostic log file, its single-file ceiling and its tail truncation SHALL stay as delivered by the diagnostic log of this project.

#### Scenario: No product surface gains the band

- **WHEN** cycles are recorded with the band and the position
- **THEN** the Monitor panel and `/api/scalp/status` SHALL NOT gain the band, the position or the interpolated value
- **AND** no new route, HTML or database table SHALL be introduced

#### Scenario: The record lives in the existing diagnostic file

- **WHEN** the band and the position are written
- **THEN** they SHALL be written to the diagnostic log file already used for the scalp Jev calls
- **AND** the file SHALL keep its single-file size ceiling and oldest-first tail truncation

#### Scenario: The read-only ruler keeps reading

- **WHEN** the cycle record gains the band and the position
- **THEN** the record prefix `scalp cycle refused` and the adjacency `user= … skip_reason=` SHALL be preserved
- **AND** the read-only ruler of the project SHALL keep reading the file without changes
