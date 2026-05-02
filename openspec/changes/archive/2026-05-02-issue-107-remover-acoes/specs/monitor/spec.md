## MODIFIED Requirements

### Requirement: Monitor MUST provide an Asset Type filter
The Monitor page (`/monitor`) MUST NOT provide an Asset Type filter while the MVP is crypto-only.

#### Scenario: Open monitor
- **WHEN** the user opens `/monitor`
- **THEN** the Monitor MUST display only crypto opportunities whose symbol contains `/`
- **AND** the Monitor MUST NOT expose a stocks option

## REMOVED Requirements

### Requirement: Asset Type filter MUST not require persistence
**Reason**: The Asset Type filter is removed from Monitor for the crypto-only MVP.
**Migration**: No persistence is required; Monitor always applies the crypto-only view state.
