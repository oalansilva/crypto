## MODIFIED Requirements

### Requirement: Provide NASDAQ-100 ticker universe
The system MUST NOT expose the NASDAQ-100 ticker universe while the MVP is crypto-only.

#### Scenario: Fetch NASDAQ-100 ticker list
- **WHEN** the UI or a client requests the NASDAQ-100 universe
- **THEN** the system MUST return an unavailable response explaining that stocks are disabled for the MVP

### Requirement: Universe is stable and versioned
The system MUST keep any stored NASDAQ-100 artifact out of operational MVP selection flows.

#### Scenario: Update NASDAQ-100 list
- **WHEN** the NASDAQ-100 list needs updating while stocks are disabled
- **THEN** it MUST NOT be exposed in Combo Configure or trading workflows until a future stocks reactivation change
