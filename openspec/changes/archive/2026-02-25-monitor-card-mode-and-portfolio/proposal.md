## Why

The Monitor dashboard is now card-based and mobile-friendly, but it still shows more information than needed for day-to-day checking. Alan wants to:

1) Make Monitor open directly into the card-based experience.
2) Reduce noise by defaulting to a smaller subset of favorites ("in portfolio")
3) Allow toggling, per card, between **Price view** (candles) and **Strategy view** (current strategy metrics/status)
4) Persist these preferences in the backend so they survive device/browser changes.

## What Changes

- Add an "In Portfolio" flag that can be toggled by the user for favorites symbols.
- Default Monitor card list to show only symbols flagged as In Portfolio.
- Add a per-card toggle icon to switch between:
  - Price view (candles + basic price metrics)
  - Strategy view (strategy status/metrics already present today)
- Persist per-symbol card view mode and the In Portfolio flag in the backend.

## Capabilities

### New Capabilities
- `monitor-portfolio-watchlist`: Mark favorites symbols as "In Portfolio" and default the Monitor list to that subset.
- `monitor-card-view-mode`: Persist per-symbol card mode (price vs strategy).

### Modified Capabilities
- `frontend-ux`: Update Monitor UX to use the new defaults and toggles.
- `backend`: Store and expose the new per-symbol preferences.

## Impact

- Backend: database schema update for storing monitor preferences.
- Frontend: Monitor card UI changes + new toggle controls.
- Tests: backend integration tests for preferences API + Playwright E2E for toggling and persistence.
