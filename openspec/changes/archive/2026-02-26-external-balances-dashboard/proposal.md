## Why

We need a single place in the app to view external account balances/positions pulled via API, starting with Binance Spot. This reduces manual checks and enables future consolidation (e.g., IBKR once live access is enabled).

## What Changes

- Add a new UI page to display **external balances snapshot**.
- Add backend endpoints to fetch **Binance Spot balances** using stored API credentials (read-only).
- Do not store trade history or place orders.

## Capabilities

### New Capabilities
- `external-balances`: Fetch and display external balances (starting with Binance Spot) in a dashboard.

### Modified Capabilities
- (none)

## Impact

- Backend: new endpoints + secret management (Binance API key/secret), read-only.
- Frontend: new page to render balances.
- Ops: requires setting env vars on the server.
