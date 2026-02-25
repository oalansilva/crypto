## Context

The Monitor experience is now card-based and includes a price-focused dashboard (candles) plus strategy information. Users want to reduce noise by defaulting the list to a smaller subset of favorites they actively hold/monitor ("In Portfolio").

Additionally, users want to toggle each symbol card between Price vs Strategy content, and for both the In Portfolio flag and per-card mode to be persisted in the backend (not local-only), so preferences survive device/browser changes.

Constraints:
- Data set is derived from Favorites.
- Preferences are per-symbol (Monitor operates on symbol cards).
- Must keep UX simple and mobile-friendly.

## Goals / Non-Goals

**Goals:**
- Persist per-symbol Monitor preferences:
  - `in_portfolio` boolean
  - `card_mode` enum (price|strategy)
- Default Monitor list to "In Portfolio" subset.
- Allow user to switch list filter between In Portfolio and All.
- Provide a per-card toggle icon to switch card mode.
- Ensure preferences are persisted and loaded from backend.

**Non-Goals:**
- User accounts / multi-user auth model.
- Complex watchlists beyond Favorites.
- Full TradingView-like customization.

## Decisions

1) Data model: new table for monitor preferences
- Decision: add a new SQLite table (e.g., `monitor_preferences`) keyed by symbol with columns:
  - `symbol` (primary key)
  - `in_portfolio` (bool)
  - `card_mode` (text)
  - timestamps (optional)
- Rationale: avoids overloading the favorites schema and keeps preferences separate.

2) API shape
- Decision: expose simple REST endpoints:
  - `GET /api/monitor/preferences` -> map keyed by symbol
  - `PUT /api/monitor/preferences/{symbol}` -> update one symbol preference
- Rationale: minimal to implement and easy for UI.

3) UI persistence behavior
- Decision: on Monitor load:
  - fetch Favorites
  - fetch preferences
  - compute derived card list
- Rationale: ensures stable UI and no duplication.

4) Defaults
- Decision:
  - default filter: In Portfolio
  - default per-card mode: Price
  - default in_portfolio: false
- Rationale: reduce noise and align with requested behavior.

## Risks / Trade-offs

- [Risk] Preferences table requires migration/initialization → Mitigation: create table on startup (like existing DB init) and keep schema minimal.
- [Risk] Symbol normalization inconsistencies (case, whitespace) → Mitigation: normalize symbols in backend (`strip()` and keep exact casing used in favorites) and in UI.
- [Risk] Additional API calls on load → Mitigation: keep endpoints lightweight and cache in UI state.

## Migration Plan

1) Add DB table + API endpoints.
2) Add frontend integration (fetch prefs, default filter, per-card toggle).
3) Add backend integration tests (preferences API) and Playwright E2E tests.
4) Deploy; verify Monitor defaults and persistence.

Rollback: revert frontend to local-only behavior and ignore prefs endpoints; table can remain.

## Open Questions

- Whether to store preferences per symbol or per favorite (strategy+symbol). Current decision is per-symbol.
- Whether to default the active view (price/strategy) per symbol or globally. Current decision is per symbol only.
