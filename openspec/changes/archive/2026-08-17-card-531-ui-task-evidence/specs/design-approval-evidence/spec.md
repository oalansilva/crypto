## ADDED Requirements

### Requirement: Verify records prototype comparison for UI cards
For `UI impact: affected`, design-approval evidence at verify/Done SHALL include the result of comparing the delivered UI to the approved prototype.

#### Scenario: Missing comparison at verify
- **WHEN** verify runs without that comparison record
- **THEN** the gate fails and Done is not allowed
