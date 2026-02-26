# monitor-candles-async-ui

## Status
- PO: done
- DEV: done
- QA: not started
- Alan (Stakeholder): not reviewed

## Decisions (locked)
- Goal: Make Monitor card candle timeframe switching optimistic + non-blocking (especially on mobile), with clear chart-only loading feedback.
- Surface (mobile/desktop): Monitor cards (OpportunityCard) candle chart timeframe control.
- Defaults:
  - Keep current default timeframe.
  - UI candles default limit: 120.
- Data sources: Existing candles fetch endpoint (no backend changes expected).
- Persistence: Client-side in-memory cache keyed by `symbol+timeframe` (no localStorage unless later requested).
- Performance limits:
  - Must cancel in-flight requests (last-click wins).
  - Must use in-memory cache to reduce refetch.
  - Must not trigger full-history backfills for UI candles (bounded by timeframe+limit).
  - While fetching candles, the card must remain interactive: scroll must work; ⭐ Portfolio toggle and Price↔Strategy toggle must remain clickable.
- Non-goals: Backend refactors; cross-session caching; changing chart library.

## Links
- OpenSpec viewer: openspec/changes/monitor-candles-async-ui/specs/monitor-candles-async-ui/spec.md
- PT-BR review (viewer): openspec/changes/monitor-candles-async-ui/review-ptbr.md
- PR: (none)
- CI run: (run `pnpm test:e2e` / GH Actions if configured)
- Implementation commit: (pending commit in repo)

## Notes
- Spec mentions: optimistic timeframe switch, chart-area loading indicator, request cancellation, in-memory cache by `symbol+timeframe`.

## Next actions
- [x] PO: Confirm/record candle fetch bounds (limit) + acceptance criteria for “non-blocking” interaction (what must remain clickable) and lock them above.
- [x] DEV: Implement optimistic timeframe switch with request cancellation + cache; add chart-only loading indicator.
- [ ] QA: Add/adjust Playwright E2E to assert timeframe switching doesn’t block card interactions + shows loading indicator; verify last-click-wins behavior.
- [ ] Alan: Review UX expectations on mobile (loading indicator placement + what stays interactive) and approve.
