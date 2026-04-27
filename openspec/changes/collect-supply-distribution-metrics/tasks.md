## 1. OpenSpec And Coordination

- [x] 1.1 Create proposal, design, spec, and tasks for supply distribution.
- [x] 1.2 Use project skills and subagents for mapping, implementation validation, and review when applicable.
- [x] 1.3 Record the alert semantics and non-goals in the OpenSpec artifacts.

## 2. Glassnode Connector

- [x] 2.1 Add Glassnode endpoint mappings for entity supply bands and long-term holder supply.
- [x] 2.2 Preserve existing API key, cache, rate-limit, asset validation, and provider error behavior.

## 3. Backend Domain Service

- [x] 3.1 Add supply distribution service using the existing Glassnode connector.
- [x] 3.2 Normalize `basis=entity`, `window=24h|7d|30d`, and fixed daily interval.
- [x] 3.3 Aggregate band latest, previous, change, change percent, and share percent.
- [x] 3.4 Aggregate shrimp, whale, and hodler cohorts.
- [x] 3.5 Emit `whale-alert` when whale supply movement is at least `1000 BTC` in absolute value.
- [x] 3.6 Keep empty, sparse, and non-numeric series valid without crashing.

## 4. API Surface

- [x] 4.1 Add `GET /api/onchain/glassnode/{asset}/supply-distribution`.
- [x] 4.2 Return bands, cohorts, whale movement, alerts, sources, cache status, and query metadata.
- [x] 4.3 Map validation/config/rate-limit errors to the existing Glassnode HTTP statuses.

## 5. Frontend Dashboard

- [x] 5.1 Add protected `/supply-distribution` dashboard route and navigation entry.
- [x] 5.2 Render wallet/entity bands, cohorts, whale movement, alerts, loading, empty, and error states.
- [x] 5.3 Add window controls for `24h`, `7d`, and `30d` that refresh the API query.

## 6. Validation

- [x] 6.1 Add unit tests for connector mappings.
- [x] 6.2 Add unit tests for service aggregation, cohorts, threshold, boundary, and sparse payloads.
- [x] 6.3 Add route tests for payload and error mapping.
- [x] 6.4 Add frontend test for dashboard render, alert state, and window switching.
- [x] 6.5 Run OpenSpec validation, targeted backend tests, frontend build/test, and formatting checks.
