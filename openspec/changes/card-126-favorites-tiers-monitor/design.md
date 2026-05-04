## Overview

Reuse the existing `FavoriteStrategy.tier` field and `/api/favorites/{id}` PATCH contract. The change is primarily frontend behavior: common users can access Favorites, assign tier through a star control, and then Monitor uses the backend's existing common-user tier filter (`1,2,3`) as the source of visible strategies.

## Decisions

- Keep the persisted model unchanged: `tier = 1 | 2 | 3 | null`.
- Present tier as stars in Favorites:
  - `tier=1` renders `★★★`
  - `tier=2` renders `★★`
  - `tier=3` renders `★`
  - `null` renders empty stars and excludes the strategy from common-user Monitor.
- Keep admin workflow available, including strategy details and existing operational actions.
- For common users, hide controls that lead to admin-only strategy workflows or protected details, including export, find-new, compare, delete, raw config, detailed backtest results, and Trader chat from Favorites.
- In Monitor, common users use the API-filtered tiered list directly. The local Monitor favorite preference remains admin/operator-only UI.

## Risks

- Existing common-user accounts only see favorites owned by their user id. This change assumes user favorites are already provisioned or saved for the user.
- The route change makes `/favorites` visible to all authenticated users, so the UI must not rely on backend redaction alone for protected technical details.

## Validation

- Build frontend.
- Run focused backend or frontend tests where available.
- Validate OpenSpec change and affected specs.
