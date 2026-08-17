## ADDED Requirements

### Requirement: Apply handoff records prototype consultation
When `UI impact: affected`, design-approval evidence for implementation SHALL include the recorded consultation of the approved prototype, not only the Design column visit.

#### Scenario: Approval exists but prototype was not consulted at apply
- **WHEN** the card is in `Pronto para Dev` but apply starts without loading the prototype
- **THEN** implementation of UI remains blocked until the consultation is recorded
