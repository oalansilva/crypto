## Why

Card #99 reports that Monitor E2E tests still assert card controls while redesigned table detail rows are collapsed or hidden. This creates noisy failures and weak regression coverage for the current Monitor UI.

## What Changes

- Render Monitor detail card rows only when a table row is expanded.
- Add accessible expanded state to table rows and row toggle controls.
- Update Monitor E2E tests to validate row content through current table selectors and explicit expansion.
- Keep product behavior unchanged for users.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `frontend-ux`: Monitor table/detail E2E coverage follows the current collapsed-row interaction model.

## Impact

- `frontend/src/components/monitor/MonitorStatusTab.tsx`
- Monitor Playwright tests under `frontend/tests/e2e/`
