## Context

The handler and service for supply distribution already exist, but the prior test coverage called the Python handler directly. That leaves a gap: a router registration or path mismatch can still produce 404 in the app while unit tests pass.

## Goals / Non-Goals

**Goals:**
- Prove `/api/onchain/glassnode/{asset}/supply-distribution` is registered as an HTTP route.
- Keep provider/configuration errors distinct from missing-route errors.
- Preserve the existing response contract.

**Non-Goals:**
- Do not mock or bypass missing Glassnode credentials in production runtime.
- Do not change the Supply Distribution UI.
- Do not introduce a new on-chain API path.

## Decisions

- Add route-level coverage with a FastAPI `TestClient` app that includes the on-chain router. This catches missing route registration and path mismatches that direct handler tests miss.
- Monkeypatch the supply distribution service in the route test to avoid external Glassnode calls and focus the test on HTTP routing behavior.
- Treat live `503 GLASSNODE_API_KEY is required` as acceptable for route availability because it proves the endpoint exists and the failure is configuration, not 404.

## Risks / Trade-offs

- A router-level test does not prove the production process is restarted. Mitigation: run `./restart` before moving to Done and capture live HTTP status after restart.
