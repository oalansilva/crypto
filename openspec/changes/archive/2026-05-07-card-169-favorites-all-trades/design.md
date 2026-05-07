## Context

Favorites currently assembles `/combo/results` state from saved or regenerated favorite trades, current candles, and Monitor `signal_history`.
Card #168 made Monitor sync authoritative for visible trades by replacing the recovered favorite trade list when Monitor returns any signal history. That is correct for current signal freshness, but wrong for Favorites history review because Monitor may only expose a shorter operational sequence.

## Goals / Non-Goals

**Goals:**

- Preserve all recoverable favorite trades in the result payload opened from `/favorites`.
- Still fetch current candles and Monitor opportunities so the result view uses fresh market context.
- Keep chart markers derived from the same complete trade list rendered by the table.
- Preserve protected common-user redaction.

**Non-Goals:**

- Change Monitor card behavior.
- Change backend Favorites or Opportunities API contracts.
- Recompute portfolio metrics beyond the existing result-page derived metrics.

## Decisions

- Merge Monitor signal trades with recovered favorite trades instead of replacing the recovered list.
  - Rationale: Favorites owns historical review; Monitor owns operational state.
  - Alternative considered: remove Monitor sync entirely from Favorites. Rejected because fresh current signals remain useful and were requested in #168.

- Deduplicate merged trades by entry time, exit time, prices, and type.
  - Rationale: the same trade can appear in saved/regenerated history and Monitor signal history.
  - Alternative considered: append without dedupe. Rejected because duplicate markers and rows would confuse users.

- Keep recovered favorite trades first, then add only non-duplicate Monitor trades.
  - Rationale: saved/regenerated history is the broadest source and must not be reduced.
  - Alternative considered: prefer Monitor trades when duplicate. Rejected because Monitor trade rows have fewer historical fields.

## Risks / Trade-offs

- Monitor signal history can describe an open trade not present in saved history -> It will appear as an extra open marker, while the table still filters closed trades as before.
- If two independent trades share identical entry/exit times and prices -> dedupe can collapse them. This is unlikely for strategy result trades and prevents the more common duplicate-source problem.
- Existing result metrics are derived from visible closed trades where possible -> merged trades may change displayed totals only when Monitor adds genuinely missing closed trades.
