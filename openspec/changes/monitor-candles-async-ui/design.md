## Context

The Monitor screen includes per-symbol candlestick charts. Switching timeframes currently triggers a fetch that can feel like it freezes the UI on mobile. This is typically caused by:
- synchronous UI state updates that block interactions
- long-running fetches without localized feedback
- multiple rapid clicks producing overlapping requests and re-renders

We want a responsive, mobile-friendly interaction where timeframe switching is optimistic and non-blocking.

## Goals / Non-Goals

**Goals:**
- Immediate UI response when selecting timeframe (optimistic selection).
- Localized loading feedback confined to the chart area.
- Cancel in-flight requests when the user changes timeframe again.
- Cache recent candles per symbol/timeframe to reduce repeat latency.

**Non-Goals:**
- Backend performance tuning or new endpoints.
- Persisting chart cache across reloads.
- Pixel-perfect chart animations.

## Decisions

1) Use per-symbol AbortController
- Decision: keep an AbortController per symbol and abort it on each new timeframe selection.
- Rationale: ensures last-click-wins behavior and prevents unnecessary state churn.

2) Optimistic UI + localized loading
- Decision: update selected timeframe immediately and only show a small spinner/skeleton overlay inside the chart container.
- Rationale: maintains responsiveness and avoids full-card or full-page blocking.

3) In-memory cache
- Decision: store candles in a module-level Map keyed by `symbol|timeframe`.
- Rationale: avoids refetching when toggling back and forth; keeps scope small.

4) E2E coverage
- Decision: add/extend Playwright E2E tests to validate that switching timeframe does not block other interactions and that loading is localized.
- Rationale: prevents regressions and catches UI freezes.

## Risks / Trade-offs

- [Risk] Cache could show stale candles briefly → Mitigation: optional background refresh; show a subtle “updated” timestamp.
- [Risk] Abort handling could surface uncaught errors → Mitigation: treat AbortError as non-error and ignore.
- [Risk] Increased complexity in OpportunityCard → Mitigation: isolate fetch/caching logic in a helper hook/module.

## Migration Plan

1) Implement async UI improvements in frontend.
2) Update E2E tests.
3) Deploy; verify on mobile with a few symbols/timeframes.

Rollback: revert the frontend commit(s); backend remains unchanged.

## Open Questions

- Should we background-refresh cached candles automatically?
- Should we add a max cache size/TTL?
