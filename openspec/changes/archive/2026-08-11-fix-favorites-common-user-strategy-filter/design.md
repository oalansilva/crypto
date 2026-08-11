## Context

Favorites already redacts protected entries for common users by replacing `strategy_name` and parameter values. The current Favorites UI derives the Strategy filter from the displayed strategy label, so when the API returns the same generic protected label for every protected favorite, common users cannot filter distinct protected strategies.

## Goals / Non-Goals

**Goals:**

- Provide a distinct safe `strategy_display_name` for protected Favorites entries.
- Reuse the safe strategy label when sending a protected favorite to the analysis/chart route.
- Keep `strategy_name` and `parameters` redacted for common users.
- Reuse the existing public display-name normalization used by Monitor protected payloads.
- Keep Favorites filters derived from strategy labels only, not favorite names, symbols, or timeframes.

**Non-Goals:**

- Expose raw internal strategy identifiers to common users.
- Change database schema, authorization rules, or admin behavior.
- Add new UI controls beyond the existing Strategy filter.

## Decisions

- Use `strategy_display_name` as the safe filter/display label for protected Favorites entries. This preserves the redacted `strategy_name` contract while giving the frontend a filterable label.
- Reuse `_public_strategy_display_name` for Favorites redaction. This keeps protected Favorites and Monitor behavior aligned and avoids a second label formatter.
- Keep filter matching and favorite analysis `template_name` handoff on `getFavoriteStrategyLabel(fav)`. Once the backend provides distinct safe labels, the existing frontend surfaces can display the same safe strategy name in both the filter and chart title.

## Risks / Trade-offs

- Safe labels can still reveal a human-readable strategy family. Mitigation: expose only normalized public labels, not parameters, indicators, raw code identifiers, or technical internals.
- Existing tests expecting the generic protected option need updates. Mitigation: adjust focused backend and Playwright assertions to the new safe-display contract.
