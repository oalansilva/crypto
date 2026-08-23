# discovery-promotion Delta

## ADDED Requirements

### Requirement: Reject promotion of a discarded result

The system SHALL reject promotion when the result is `discarded`. The UI SHALL not offer an enabled Promote control for discarded rows because they are omitted from the default leaderboard.

#### Scenario: Promote discarded result via API

- **WHEN** a client posts promotion for a `discarded` `result_id`
- **THEN** the server rejects the request
- **AND** no favorite is created
