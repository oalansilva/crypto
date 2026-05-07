## Context

The Favorites page renders two layouts: a desktop table and mobile cards. The desktop table has `min-width: 1320px` inside an `overflow-x: auto` shell, so common desktop widths can require horizontal scrolling even when the essential workflow only needs symbol, strategy, tier, direction, timeframe, key metrics, and actions.

## Goals / Non-Goals

**Goals:**
- Remove horizontal scrolling as the normal Favorites workflow on common desktop widths.
- Keep the dense operational table on desktop and the existing cards on tablet/mobile.
- Preserve primary action access and key trading metrics.
- Follow `DESIGN.md` tokens already present in `favorites-workbench`: near-black surfaces, Binance yellow actions, trading green/red semantics, compact 8px radii, flat hairlines.

**Non-Goals:**
- No backend, API, filtering, ordering, or data model change.
- No removal of favorite data from export or analysis views.
- No redesign of other pages.

## Decisions

- Use responsive column priority instead of replacing the desktop table with cards. This keeps desktop scan density and changes only the crowded grid behavior.
- Mark advanced metric columns with explicit CSS classes and hide them at defined breakpoints. Primary columns remain visible: tier, symbol, strategy, direction, timeframe, sharpe, trades, return, and actions.
- Keep period/stop/max drawdown visible longer than the deepest advanced columns, then hide them on smaller desktop widths to prevent overflow.
- Keep mobile cards active below `1024px`, matching the existing breakpoint and avoiding a second mobile pattern.

## Risks / Trade-offs

- Advanced metrics are not visible in the common desktop table at all widths -> they remain available on wide screens, export, and the full analysis action.
- CSS-only responsive behavior can drift if new columns are added -> E2E overflow checks cover the current grid at representative desktop/mobile widths.
