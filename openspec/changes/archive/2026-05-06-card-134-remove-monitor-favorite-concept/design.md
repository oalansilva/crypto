## Context

`MonitorStatusTab` still keeps a separate Monitor-local favorite concept: localStorage key `crypto-monitor-favorites-v1`, `/monitor/strategy-preferences` reads/writes, a `Favoritos` list filter, favorite counters, and star icon actions for admin/operator rows. The product now has `/favorites` as the curation surface, including star/tier ranking used by Monitor visibility.

## Goals / Non-Goals

**Goals:**
- Remove favorite management controls and filters from the Monitor screen.
- Remove Monitor-local favorite state, localStorage usage, and `/monitor/strategy-preferences` calls from `MonitorStatusTab`.
- Keep read-only tier/star labels in Monitor rows because they represent Favorites ranking.
- Keep the Favorites page as the only UI for adding, removing, or ranking favorites.
- Update focused E2E coverage.

**Non-Goals:**
- Remove `/monitor/strategy-preferences` backend routes in this card.
- Change Favorites page behavior.
- Change backend opportunity source or tier filtering.
- Archive this OpenSpec change during card implementation.

## Decisions

1. Delete Monitor-local favorite state instead of hiding only the buttons.
   - Rationale: the acceptance criteria explicitly reject a second favorite list in storage/preferences.
   - Alternative considered: keep the state but hide UI. Rejected because stale hidden state would keep a second curation path alive.

2. Preserve `tier`/star display in Monitor.
   - Rationale: stars are not a Monitor-local favorite action; they are the current Favorites ranking used to decide what appears.

3. Keep `in_portfolio` controls separate from favorites.
   - Rationale: portfolio/watchlist is an operational Monitor concern and remains distinct from Favorites curation.

4. Scope code changes to `MonitorStatusTab` and affected tests.
   - Rationale: `MonitorDashboardTab` is not currently mounted by `MonitorPage`, and backend cleanup can be a separate hardening change if needed.

## Risks / Trade-offs

- [Risk] Admin loses a quick Monitor-only favorite shortcut. -> Mitigation: Favoritos is the canonical place for curation and ranking.
- [Risk] Existing tests rely on the favorite filter/toggle. -> Mitigation: update tests to assert absence of those controls and preserve star/tier rendering.
- [Risk] Backend route remains unused. -> Mitigation: leave route in place to avoid broader API cleanup in this UI-focused card.
