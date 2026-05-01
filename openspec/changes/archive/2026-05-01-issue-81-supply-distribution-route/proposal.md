## Why

Issue #81 reports that the live backend returned 404 for `GET /api/onchain/glassnode/BTC/supply-distribution?basis=entity&window=24h`, breaking the Supply Distribution screen. The backend must expose this endpoint consistently so the UI receives data or a meaningful upstream/configuration error, never a missing-route response.

## What Changes

- Add HTTP-level route regression coverage for the supply distribution endpoint.
- Verify the live runtime no longer returns 404 for the reported URL.
- Keep existing service behavior for provider/configuration errors.

## Capabilities

### New Capabilities

### Modified Capabilities
- `backend`: on-chain supply distribution route availability must be covered as an HTTP endpoint.

## Impact

- Backend route tests for `app.routes.onchain_metrics`.
- No database migration, API shape change, or frontend contract change expected.
