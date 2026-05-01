## Why

The Wallet page currently looks visually disconnected from the supplied Crypto Workbench template and has weak scanability for balances, credentials, filters, totals, and mobile inspection. Card #103 asks for the Wallet layout to be refactored against the attached template so the account workflow feels consistent with the rest of the trading workspace.

## What Changes

- Refactor the `/external/balances` Wallet page into the supplied workbench-style layout.
- Add compact KPI tiles for total value, visible assets, partial PnL, and weighted performance.
- Rework Binance credential status and inputs into a clear read-only credential panel.
- Rework search, dust threshold, sorting, reset, and export controls into a compact filter toolbar.
- Rework balances into a desktop table with asset identity, values, PnL, allocation share, and mobile cards.
- Preserve existing Binance credential API and read-only balance endpoint behavior.

## Capabilities

### New Capabilities

### Modified Capabilities
- `external-balances`: Wallet UI presentation and responsive behavior are updated to match the supplied template while preserving existing read-only balance behavior.

## Impact

- Affected frontend: `frontend/src/pages/ExternalBalancesPage.tsx`.
- Affected tests: Wallet E2E and frontend build.
- No backend API contract change expected unless implementation uncovers missing data already required by the layout.
