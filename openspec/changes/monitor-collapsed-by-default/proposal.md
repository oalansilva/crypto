## Why

Monitor currently opens every strategy detail row by default, which makes the screen too tall and noisy. Users should scan strategy rows first and expand only the one they want to inspect.

## What Changes

- Make Monitor strategy rows collapsed by default.
- Keep row click and chevron expansion behavior.
- Update affected E2E tests to explicitly expand detail rows when they need detail-card assertions.

## Capabilities

### New Capabilities
- `monitor-collapsed-rows`: Monitor strategy details are collapsed until the user expands a row.

### Modified Capabilities
- `opportunity-monitor`: Monitor keeps existing opportunity data but changes the default detail visibility.

## Impact

- Frontend: `MonitorStatusTab` row expansion default.
- Tests: affected Monitor E2E expectations.
