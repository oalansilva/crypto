## 1. Planning & Scaffolding

- [ ] 1.1 Identify backend module location for spread detection service
- [ ] 1.2 Define API contract (request params, response schema) for spread detection

## 2. Backend Implementation

- [ ] 2.1 Implement CCXT WebSocket order-book streamer for USDT/USDC per exchange
- [ ] 2.2 Implement spread calculation across exchanges (best-ask buy, best-bid sell)
- [ ] 2.3 Apply threshold filtering and sort opportunities by spread desc

## 3. API Wiring

- [ ] 3.1 Add endpoint (e.g., GET /api/arbitrage/spreads) with query params for exchanges and threshold
- [ ] 3.2 Add response serialization with buy/sell venues, prices, spread %, timestamps

## 4. Tests

- [ ] 4.1 Unit test spread calculation with deterministic price fixtures
- [ ] 4.2 API test for threshold filtering and response shape

## 5. Documentation

- [ ] 5.1 Update internal docs or API reference with endpoint usage

> Note: Use project skills (.codex/skills) when applicable (architecture, tests, debugging, frontend).
