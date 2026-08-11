## 1. OpenSpec And Contract

- [x] 1.1 Create proposal, design, spec delta, and tasks.
- [x] 1.2 Define supported windows, endpoints, and aggregation rules.

## 2. Backend Service

- [x] 2.1 Add Glassnode exchange flow endpoint mapping.
- [x] 2.2 Implement `24h`, `7d`, and `30d` window resolution.
- [x] 2.3 Aggregate inflow, outflow, and netflow by exchange.
- [x] 2.4 Aggregate inflow, outflow, and netflow totals.
- [x] 2.5 Preserve API key, rate-limit, and cache behavior from the existing connector.

## 3. API Surface

- [x] 3.1 Add endpoint to fetch exchange flows by asset/window.
- [x] 3.2 Map provider/config/rate-limit errors to existing HTTP statuses.

## 4. Validation

- [x] 4.1 Add unit tests for object payload aggregation by exchange.
- [x] 4.2 Add unit tests for scalar total fallback.
- [x] 4.3 Add route tests for supported windows and error mapping.
- [x] 4.4 Run OpenSpec validation and backend/frontend checks.
