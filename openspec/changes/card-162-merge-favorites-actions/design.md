## Context

`FavoritesDashboard` currently exposes two admin-only actions per favorite: `View Trades` opens a modal backed by saved/regenerated trades, while `View Results` reruns the combo backtest and navigates to `/combo/results`. The results page already displays consolidated metrics, chart, and a trade list, so the split creates duplicated analysis entry points.

## Goals / Non-Goals

**Goals:**
- Provide one admin analysis CTA per favorite in desktop and mobile Favorites layouts.
- Keep the existing combo result page as the consolidated destination for metrics, chart, and trades.
- Preserve the trade-recovery behavior from `GET /api/favorites/{id}/trades` when saved trade history is missing.
- Surface metric mismatch as a non-blocking warning in the result page.

**Non-Goals:**
- Change Favorites API contracts.
- Expose protected favorite internals to non-admin users.
- Redesign the combo results page beyond a small warning banner.

## Decisions

- Use one CTA named `Analisar` with `title="Ver análise completa"` because it describes the combined result/trade workflow without duplicating button intent. Alternative considered: keep two buttons with clearer labels; rejected because the card asks to remove the duplicated choice.
- Keep `/combo/results` as the unified destination because it already shows the consolidated metrics and `List of trades`. Alternative considered: build a new modal; rejected because it would duplicate the richer result screen.
- Fetch favorite trades before navigation when saved trades are absent but summary metrics indicate trades exist. The loaded trades are injected into the result payload so the result page displays the same recovered history the old trades modal would show.
- Pass a lightweight warning through navigation state when regenerated trades do not match saved summary metrics. The result page renders this as a non-blocking banner.

## Risks / Trade-offs

- Result and recovered trades can diverge from saved summary metrics -> show warning and keep analysis accessible.
- Backtest and trade-recovery requests add latency to the single CTA -> use one loading state per favorite and avoid extra request when saved trades already exist.
- Protected favorites could leak internals through the unified action -> keep the existing protected guard before any analysis request.
