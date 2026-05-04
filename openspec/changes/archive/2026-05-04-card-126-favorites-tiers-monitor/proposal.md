## Why

Common users need to choose which admin-generated strategies they want monitored without seeing protected strategy internals. The existing Favorites route is admin-only and the Monitor common-user experience can still be narrowed by portfolio/local favorite filters instead of the star tier chosen on Favorites.

## What Changes

- Allow common users to open the Favorites page and assign monitoring priority through stars.
- Map stars to existing tier values: 3 stars = tier 1, 2 stars = tier 2, 1 star = tier 3, no stars = not monitored.
- Keep protected strategy internals hidden from common users on Favorites and Monitor.
- Make common-user Monitor show only tiered favorite strategies returned by the backend, without requiring portfolio membership or a separate Monitor favorite toggle.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites is no longer admin-only; common users can manage tier stars while protected internals stay hidden.
- `monitor`: Common-user Monitor is driven by tiered Favorites selection and shows only strategies marked with stars.

## Impact

- Frontend route/access control: `frontend/src/App.tsx`, `frontend/src/components/AppNav.tsx`
- Favorites UI: `frontend/src/pages/FavoritesDashboard.tsx`
- Monitor UI/filtering: `frontend/src/components/monitor/MonitorStatusTab.tsx`
- Existing API behavior: `/api/favorites`, `/api/opportunities`, `/api/monitor/strategy-preferences`
