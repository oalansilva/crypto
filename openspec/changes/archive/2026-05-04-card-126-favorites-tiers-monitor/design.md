## Overview

Reuse the existing `FavoriteStrategy.tier` field and `/api/favorites/{id}` PATCH contract. The change is primarily frontend behavior: common users can access Favorites, assign tier through a star control, and then Monitor uses the backend's existing common-user tier filter (`1,2,3`) as the source of visible strategies.

## Decisions

- Keep the persisted model unchanged: `tier = 1 | 2 | 3 | null`.
- Treat admin favorites as the common-user strategy catalog. Common-user star selections are stored per user in `monitor_strategy_preferences.tier`, not in the admin's `favorite_strategies.tier`.
- Present tier as stars in Favorites:
  - `tier=1` renders `★★★`
  - `tier=2` renders `★★`
  - `tier=3` renders `★`
  - `null` renders empty stars and excludes the strategy from common-user Monitor.
- Keep admin workflow available, including strategy details and existing operational actions.
- For common users, hide controls that lead to admin-only strategy workflows or protected details, including export, find-new, compare, delete, raw config, detailed backtest results, and Trader chat from Favorites.
- In Monitor, common users use the API-filtered tiered list directly, with tiers overlaid from their own `monitor_strategy_preferences.tier`. The local Monitor favorite preference remains admin/operator-only UI.
- Align the Favorites visual surface with the provided `crypto.2.zip` reference: operational header, three star summary cards, segmented tier chips, compact filters/search, dense strategy table on desktop, and scannable strategy cards on mobile.
- Use `DESIGN.md` as the visual source of truth for Favorites: Binance yellow primary action/chips, documented dark surfaces, hairline borders, 6-8px radii, modest typography weights, and trading green/red semantics.

## Risks

- Common-user accounts do not own the admin-generated favorites. The backend overlays each user's `monitor_strategy_preferences.tier` on the admin catalog so the user can star strategies without mutating admin data.
- The route change makes `/favorites` visible to all authenticated users, so the UI must not rely on backend redaction alone for protected technical details.

## Validation

- Build frontend.
- Run focused backend or frontend tests where available.
- Validate OpenSpec change and affected specs.
