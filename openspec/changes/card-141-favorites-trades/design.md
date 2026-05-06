## Context

Favorites can show `total_trades` while older rows have no `metrics.trades`. The current UI treats that as "no saved trades", so the user cannot inspect trades even when the stored summary proves the strategy produced trades.

## Goals / Non-Goals

**Goals:**
- Recover missing favorite trades from stored strategy parameters.
- Reuse the combo backtest engine so regenerated trades and metrics use the same business logic as View Results.
- Compare regenerated metrics with stored favorite metrics and expose whether the favorite remains valid.
- Keep protected strategy redaction intact for non-admin users.

**Non-Goals:**
- Do not change favorite ranking, tier semantics, or Monitor logic.
- Do not expose protected strategy parameters to common users.
- Do not rewrite historical favorite metrics unless trades are missing and can be attached safely.

## Decisions

- Add `GET /api/favorites/{favorite_id}/trades` instead of overloading the list endpoint. This keeps the normal Favorites load light and regenerates only when the user asks for trades.
- Extract combo backtest execution into a reusable helper called by both `/api/combos/backtest` and the Favorites trade endpoint. This avoids duplicating signal extraction, metric calculation, and provider selection.
- Persist regenerated trades into `favorite.metrics.trades` when the row belongs to the current user or an admin is viewing their own favorite. This fixes older rows lazily without a broad migration.
- Return `metrics_match` and `metrics_deltas` so the UI and tests can detect when regenerated results no longer match stored summary metrics.

## Risks / Trade-offs

- Regeneration depends on current market data and strategy code. A strategy or data-source change can produce deltas. Mitigation: compare key metrics and return mismatch details.
- The endpoint can be slower than reading stored trades. Mitigation: only run it when saved trades are missing and persist the regenerated list.
- Protected catalog favorites contain strategy secrets. Mitigation: require strategy-secret visibility for regeneration; common users keep the protected empty-trades behavior.
