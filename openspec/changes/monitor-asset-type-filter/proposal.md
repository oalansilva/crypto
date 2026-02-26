## Why

The Monitor currently mixes crypto pairs and stock tickers in the same list, making it harder to focus on a single asset universe. A simple Asset Type filter reduces noise and improves daily usability.

## What Changes

- Add an **Asset Type** filter to `/monitor` with options: **All**, **Crypto**, **Stocks**.
- Filter affects only the current view (no persistence required).

## Capabilities

### New Capabilities
- `monitor-asset-type-filter`: Allow filtering Monitor opportunities by asset type (crypto vs stocks).

### Modified Capabilities
- (none)

## Impact

- Frontend-only change (Monitor UI filtering).
- No backend API changes.
