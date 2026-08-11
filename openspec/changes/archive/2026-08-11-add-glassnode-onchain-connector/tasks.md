## 1. OpenSpec And Contract

- [x] 1.1 Create proposal, design, spec delta, and tasks for the Glassnode connector.
- [x] 1.2 Define supported metrics, supported assets, cache TTL, and rate-limit behavior.

## 2. Backend Connector

- [x] 2.1 Add configurable Glassnode settings.
- [x] 2.2 Implement Glassnode service for MVRV, NVT, realized cap, and SOPR.
- [x] 2.3 Enforce supported assets BTC and ETH.
- [x] 2.4 Add 15-minute in-memory cache before external requests.
- [x] 2.5 Respect configured rate limit before external requests.
- [x] 2.6 Surface missing API key and upstream 429 errors clearly.

## 3. API Surface

- [x] 3.1 Add backend route to fetch Glassnode metrics by asset.
- [x] 3.2 Register route in the FastAPI app.

## 4. Validation

- [x] 4.1 Add unit tests for cache, rate limit, API key, BTC/ETH support, and 429 handling.
- [x] 4.2 Validate OpenSpec change.
- [x] 4.3 Run backend targeted tests and frontend build.
