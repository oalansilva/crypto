## Why

Monitor currently uses a mostly black/dark palette. Alan wants a refreshed look focused on a dark-green aesthetic for the Monitor screen only.

The change should preserve readability and not impact performance.

## What Changes

- Update the **Monitor** UI palette to use **dark green** as the primary dark background instead of black.
- Persist the user's Monitor theme preference in the backend.
- Default theme: **dark-green**.

## Capabilities

### New Capabilities
- `monitor-theme-preference`: Persist Monitor theme preference in the backend.

### Modified Capabilities
- `frontend-ux`: Apply the new dark-green theme styling to `/monitor`.
- `backend`: Store and serve the preference.

## Impact

- Frontend: `/monitor` styles (cards, filter bar, chart container, buttons).
- Backend: preference storage (extend monitor preferences) and API to read/update theme.
- Tests: integration test for preference API; E2E smoke to ensure theme is applied.
