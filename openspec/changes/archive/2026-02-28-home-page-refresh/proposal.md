## Why

The current Home page is effectively a single promotional entrypoint (Combo Strategies), which makes the product feel “hidden” and increases time-to-action for daily flows.
We need a clearer, more useful Home that works as a hub for the core workflows (monitoring, running strategies, checking balances, and navigating to specs/kanban).

## What Changes

- Replace the current single-CTA Home with a small **Home hub dashboard**.
- Add a **Quick Actions / Shortcuts** section to jump into the main areas:
  - Favorites Dashboard
  - Monitor
  - Combo Strategies (select / configure)
  - Strategy Lab
  - Arbitrage
  - External Balances
  - Kanban
  - OpenSpec
- Add lightweight “orientation” content on Home:
  - 1–2 lines explaining what the app is for
  - a compact “Where to start” suggestion (e.g., start with Favorites → Monitor → run a strategy)

## Capabilities

### New Capabilities
- `home`: A Home hub page that provides at-a-glance orientation and clear shortcuts into the main product workflows.

### Modified Capabilities
- (none)

## Impact

- Frontend: Home page UI structure will be updated (information architecture + navigation shortcuts).
- Design: a reusable HTML/CSS prototype will be produced for DEV to implement consistently.
- Backend: no new endpoints required for v1 (Home can be purely navigational and informational).
