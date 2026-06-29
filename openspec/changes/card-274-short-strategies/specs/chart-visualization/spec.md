## MODIFIED Requirements

### Requirement: Trade Marker Phase Is Not Inferred From Text Alone

Chart marker helpers SHALL distinguish trade phase from visual action labels.

#### Scenario: Short sell marker is an entry

- **GIVEN** a trade marker was built for a short entry
- **AND** its visible label is `VENDA`
- **WHEN** consumers ask for marker signal phase
- **THEN** the marker SHALL be classified as entry, not exit

#### Scenario: Short buy marker is an exit

- **GIVEN** a trade marker was built for a short exit or cover
- **AND** its visible label is `COMPRA`
- **WHEN** consumers ask for marker signal phase
- **THEN** the marker SHALL be classified as exit, not entry
