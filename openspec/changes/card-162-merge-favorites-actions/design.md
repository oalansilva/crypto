## Context

`FavoritesDashboard` currently exposes two admin-only actions per favorite: `View Trades` opens a modal backed by saved/regenerated trades, while `View Results` reruns the combo backtest and navigates to `/combo/results`. The results page already displays consolidated metrics, chart, and a trade list, so the split creates duplicated analysis entry points.

## Goals / Non-Goals

**Goals:**
- Provide one admin analysis CTA per favorite in desktop and mobile Favorites layouts.
- Keep the existing combo result page as the consolidated destination for metrics, chart, and trades.
- Preserve the trade-recovery behavior from `GET /api/favorites/{id}/trades` when saved trade history is missing.
- Persist the generated favorite analysis cache so the next click reopens saved history instead of regenerating it.
- Keep metric mismatch metadata internal for investigation and do not show reconstructed-history mismatch warnings in the result page.
- Keep the result page aligned to `DESIGN.md`: dark Binance canvas/surfaces with yellow primary actions and clear table contrast.

**Non-Goals:**
- Expose protected favorite internals to non-admin users.
- Redesign the combo results page beyond a small warning banner.

## Decisions

- Use one CTA named `Analisar` with `title="Ver análise completa"` because it describes the combined result/trade workflow without duplicating button intent. Alternative considered: keep two buttons with clearer labels; rejected because the card asks to remove the duplicated choice.
- Keep `/combo/results` as the unified destination because it already shows the consolidated metrics and `List of trades`. Alternative considered: build a new modal; rejected because it would duplicate the richer result screen.
- Fetch favorite trades before navigation when saved trades are absent but summary metrics indicate trades exist. The loaded trades are injected into the result payload so the result page displays the same recovered history the old trades modal would show.
- Preserve regenerated-trade mismatch metadata in favorite metrics for investigation, but keep the result page focused on actionable analysis without a user-facing mismatch banner.
- Stop running `/api/combos/backtest` from the favorite analysis CTA. `GET /api/favorites/{id}/trades` is the source for missing analysis history; saved `metrics.trades` is the fast path.
- When trade history is regenerated, persist `metrics.trades` and lightweight analysis cache fields on the favorite. If metrics differ, accept regenerated metrics as the saved summary and store previous summary/deltas as investigation metadata.
- Style the result trade table with `DESIGN.md` tokens: `#0b0e11` canvas, `#1e2329` elevated surface, `#181a20` header rows, `#2b3139` borders, `#eaecef`/`#929aa5` text, `#fcd535` primary CTA, and trading green/red for P&L.

## Risks / Trade-offs

- Result and recovered trades can diverge from saved summary metrics -> reconcile saved metrics and keep previous summary/deltas available as internal metadata.
- The fast cached path may not have chart candles for older favorites that only stored trades -> keep the result table available and show the existing no-chart state instead of regenerating unnecessarily.
- Regeneration can still add latency on the first click when history is missing -> use one loading state per favorite and avoid extra request when saved trades already exist.
- Protected favorites could leak internals through the unified action -> keep the existing protected guard before any analysis request.
