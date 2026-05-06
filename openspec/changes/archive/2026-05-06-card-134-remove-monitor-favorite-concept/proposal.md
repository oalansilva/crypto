## Why

The Monitor still contains a local favorite concept even though the Favorites screen is now the established place to choose, rank, and maintain monitored strategies. This creates two competing curation surfaces and makes the Monitor less focused on operational decisions.

## What Changes

- Remove Monitor-local favorite controls, filters, counters, storage, and API calls.
- Keep star/tier display in the Monitor as read-only classification coming from Favorites.
- Keep Monitor focused on actionable strategy status and operational inspection.
- Preserve the Favorites screen as the only place to add, remove, or rank favorite strategies.
- Update focused Monitor tests to assert absence of favorite controls while keeping tier/star visibility.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `monitor`: remove Monitor-local favorite management and favorite filters from the Monitor screen.
- `favorites`: clarify that the Favorites screen owns strategy curation and star/tier ranking used by the Monitor.

## Impact

- Frontend Monitor UI and state in `frontend/src/components/monitor/MonitorStatusTab.tsx`.
- Monitor E2E tests in `frontend/tests/e2e/monitor-card-mode-and-portfolio.spec.ts`.
- OpenSpec specs for Monitor and Favorites responsibilities.
