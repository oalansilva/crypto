## Why

The "Locked only" filter toggle and "Locked" column on the Wallet screen are unused or low-value UI elements that add visual noise and maintenance burden. Removing them simplifies the balance view and reduces confusion for users.

## What Changes

- **Remove** the "Locked only" filter toggle from the Wallet (`/external/balances`) UI
- **Remove** the "Locked" column from the balances table on the Wallet screen
- **BREAKING**: Any client code relying on the `locked` field in the Wallet API response will no longer have it surfaced in the UI (the API field itself is unchanged)

## Capabilities

### New Capabilities
_(none)_

### Modified Capabilities
- `external-balances`: Remove the "Locked only" filter UI requirement and the "Locked" column display requirement from the Wallet UI spec

## Impact

- **Frontend**: Wallet page (`/external/balances`) — remove toggle and table column
- **Spec**: `openspec/specs/external-balances/spec.md` — remove locked-only filter and locked column requirements
