## ADDED Requirements

### Requirement: Glassnode API key is configurable
The system SHALL load the Glassnode API key from runtime configuration.

#### Scenario: Missing API key fails before network call
- **GIVEN** no Glassnode API key is configured
- **WHEN** a Glassnode metric fetch is requested
- **THEN** the connector SHALL fail with a configuration error
- **AND** SHALL NOT call the external Glassnode API.

### Requirement: Connector fetches required Glassnode metrics
The system SHALL collect MVRV, NVT, realized cap, and SOPR from Glassnode for supported assets.

#### Scenario: BTC metrics collected
- **WHEN** metrics are requested for `BTC`
- **THEN** the connector SHALL request MVRV, NVT, realized cap, and SOPR from Glassnode.

#### Scenario: ETH metrics collected
- **WHEN** metrics are requested for `ETH`
- **THEN** the connector SHALL request MVRV, NVT, realized cap, and SOPR from Glassnode.

### Requirement: Connector caches responses for 15 minutes
The connector SHALL cache Glassnode metric responses for 15 minutes by metric, asset, interval, since, and until.

#### Scenario: Cache hit avoids external call
- **GIVEN** a metric was fetched less than 15 minutes ago for the same query parameters
- **WHEN** the same metric is requested again
- **THEN** the connector SHALL return the cached response
- **AND** SHALL NOT call Glassnode again.

### Requirement: Connector respects rate limits
The connector SHALL throttle outbound Glassnode requests according to configured rate limit.

#### Scenario: Consecutive calls are spaced
- **GIVEN** the configured Glassnode rate limit requires spacing between calls
- **WHEN** two uncached Glassnode requests are issued consecutively
- **THEN** the connector SHALL wait before the second outbound request.

### Requirement: Upstream rate-limit errors are explicit
The connector SHALL surface Glassnode HTTP 429 responses as rate-limit errors.

#### Scenario: Glassnode returns 429
- **WHEN** Glassnode returns HTTP 429
- **THEN** the connector SHALL raise a rate-limit error that can be returned as HTTP 429 by the API route.
