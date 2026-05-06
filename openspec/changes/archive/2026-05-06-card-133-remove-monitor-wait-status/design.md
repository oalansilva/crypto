## Context

`MonitorStatusTab` currently groups every resolved opportunity into `hold`, `wait`, or `exit`. `resolveOpportunitySignal` uses `wait` as the safe fallback for stale candles, timeframe mismatch, unknown raw status, neutral strategy state, and non-confirmed entry contexts. That fallback is technically useful, but exposing it as a main Monitor state makes non-actionable strategies look like opportunities.

The product decision for card #133 is to keep the main Monitor focused on actionable decisions. Non-actionable results may still exist in the backend payload or internal frontend resolver, but they must not appear as a primary user-facing section.

## Goals / Non-Goals

**Goals:**
- Hide `WAIT` from the main Monitor board, KPI counters, and common-user visible opportunity sections.
- Keep `HOLD` and `EXIT` visible as the actionable Monitor sections.
- Filter neutral, wait, stale, mismatched, unknown, or otherwise uncertain results out of the main visible opportunity list.
- Preserve defensive logic so uncertain rows never get promoted to `HOLD` or `EXIT`.
- Update focused Monitor tests to cover the removal of visible `WAIT`.

**Non-Goals:**
- Change backend opportunity payload shape.
- Rewrite strategy signal generation.
- Remove internal wait-like fallback logic used for safety and chart context.
- Archive this OpenSpec change during card implementation.

## Decisions

1. Keep `wait` as an internal resolver section, but exclude it from the visible board.
   - Rationale: this is safer than coercing uncertain rows into buy/sell states and avoids a larger backend contract change.
   - Alternative considered: remove `wait` from the type system. Rejected because chart/detail safety paths and stale-context handling still need a non-actionable bucket.

2. Make visible section order explicit as `hold` and `exit`.
   - Rationale: the UI should present only actionable decision groups while retaining internal computed sections for filtering and counts.
   - Alternative considered: rename `WAIT` to `Sem sinal`. Rejected because Alan explicitly asked to remove the intermediate visible status, not only improve copy.

3. Keep rated/star and strategy filters before actionability filtering.
   - Rationale: card #129 already established rated-only Monitor visibility. Card #133 only changes which resolved decision sections survive into the main board.

4. Use focused frontend tests around the resolver/UI contract.
   - Rationale: the risk is a product-state regression, so coverage should prove `WAIT`/neutral rows are not rendered as visible actionable opportunities while `HOLD` and `EXIT` remain visible.

## Risks / Trade-offs

- [Risk] Fewer rows appear in the Monitor after filtering `WAIT` out. → Mitigation: empty states already exist; this is intended because non-actionable rows are no longer opportunities.
- [Risk] Admin/operator users may lose quick visibility into neutral strategies on the main board. → Mitigation: keep internal resolver data and operator filters intact where possible, but main decision sections stay action-focused.
- [Risk] Existing tests assert three sections. → Mitigation: update focused tests and keep validation scoped to the changed Monitor behavior.
