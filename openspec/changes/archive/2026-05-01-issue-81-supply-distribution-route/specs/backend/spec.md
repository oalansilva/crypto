## ADDED Requirements

### Requirement: Supply distribution endpoint is registered
The backend SHALL expose the supply distribution endpoint at `/api/onchain/glassnode/{asset}/supply-distribution`.

#### Scenario: Route exists for BTC supply distribution
- **WHEN** an authenticated backend client requests `GET /api/onchain/glassnode/BTC/supply-distribution?basis=entity&window=24h`
- **THEN** the backend SHALL route the request to the supply distribution handler
- **AND** the response SHALL NOT be HTTP 404

#### Scenario: Provider configuration is missing
- **WHEN** the supply distribution route is registered but Glassnode credentials are unavailable
- **THEN** the backend SHALL return a service/configuration error instead of HTTP 404
