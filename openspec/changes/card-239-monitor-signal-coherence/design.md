## Context

Card #238 normalized same-candle marker rendering so the chart no longer displays independent contradictory `Compra` and `Venda` markers for one displayed candle. Card #239 is a different symptom: the chart can now show the resolved `Venda`, while the Monitor summary/current state still reports `Compra`.

The likely risk is drift between two sources:

- chart markers built from favorite trades/signal history;
- Monitor current state derived from opportunity fields such as `status`, `is_holding`, `current_signal`, `signal_history` or fallback state.

## Goals / Non-Goals

**Goals:**

- Reproduce or model the ADA/USDT 1D moving-average divergence.
- Identify whether the inconsistency is frontend resolver, API payload, persisted favorite analysis, cache or strategy calculation.
- Make Monitor summary/current-state labels converge with the latest valid chart signal for the same strategy/timeframe.
- Keep common-user labels as `Compra` and `Venda`; do not expose raw `HOLD`/`EXIT`.
- Add focused automated coverage for the resolver path.

**Non-Goals:**

- Recalibrate moving-average strategy parameters.
- Create a new strategy.
- Change financial meaning or promise an investment outcome.
- Broadly reprocess all assets/timeframes unless evidence shows a systemic backend issue.

## Decisions

- Treat chart-visible latest valid signal as the UI truth for the displayed current state when Monitor has favorite-backed trade/marker data.
  - Rationale: the user is comparing one visible Monitor state with one visible Monitor chart; those two surfaces must agree.
- Preserve backend raw status fields for classification and API compatibility.
  - Rationale: board grouping and backend contracts can still use internal `HOLD`/`EXIT` semantics while the UI label is resolved for coherence.
- Prefer a shared resolver/helper over page-local conditional copy.
  - Rationale: Monitor row, modal header and chart context must not drift again.
- Follow `DESIGN.md` without adding new visual patterns unless necessary.
  - Rationale: this is primarily behavioral coherence, not a redesign.

## Risks / Trade-offs

- If the API payload is already inconsistent, a frontend-only fix could mask backend debt. Implementation must record the diagnosed origin.
- If there are multiple valid same-day actions, the resolver must use the post-card #238 marker rule instead of reviving duplicate signals.
- Tests need stable fixtures because live market data can change.
