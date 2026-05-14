## ADDED Requirements

### Requirement: Chart modal opens with decision context visible
The Monitor chart modal SHALL expose signal context, risk/stop, and signal history in the default opening path for a Monitor opportunity.

#### Scenario: Default chart modal shows operational context
- **WHEN** a user opens the detailed chart from a Monitor opportunity
- **THEN** the modal SHALL show signal context without requiring a manual layout switch
- **AND** the modal SHALL show risk/stop information when available
- **AND** the modal SHALL show signal history when the opportunity payload includes it
