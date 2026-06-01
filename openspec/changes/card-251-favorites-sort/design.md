## Context

`FavoritesDashboard` filters crypto favorites and then sorts the list locally. The current comparator sorts by star tier first and only uses the selected metric after that. Because the mocked and real catalog commonly has different tiers, changing the `Ordenar` selector can appear broken: rows stay grouped by tier instead of moving according to Return, Sharpe, Trades, or Ret/T.

## Decision

The visible sort selector should be the primary ordering key. Tier remains a deterministic tie-breaker after the selected metric so equally-ranked metric values still have a stable, useful order.

The comparator will use normalized sortable values:

- Return: `metrics.total_return_pct`, falling back to `metrics.total_return * 100`.
- Sharpe: `metrics.sharpe_ratio`.
- Trades: the same trade count helper already used by the grid.
- Ret/T: return percentage divided by at least one trade.

All selected sort modes remain descending because the UI does not expose ascending/descending options.

## Risks

- Users who expected tier to always dominate ordering may see rows move more aggressively. This is intentional for card #251 because selecting a sort option should visibly reorder the list.
- Missing metrics must not produce unstable `NaN` comparisons. Missing numeric values will sort after real values.

## Validation

- Add Playwright coverage with deterministic Favorites API data.
- Select multiple sort options and assert first rendered rows change according to the selected metric.
- Run OpenSpec validation and the focused Favorites E2E spec.
