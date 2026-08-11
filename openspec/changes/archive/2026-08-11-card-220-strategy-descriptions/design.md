## Context

The product already separates common-user and admin visibility for strategy details. Common users receive redacted Favorites and Monitor payloads, while admin/internal flows can still inspect template names, parameters, indicator values, and raw strategy metadata.

The current public label formatter converts technical identifiers into title-cased names, and public descriptions are keyed by template name. Card #220 narrows the product requirement: generated strategies need useful, distinguishable product names and descriptions, but the public copy cannot reveal a technical recipe.

## Goals / Non-Goals

**Goals:**

- Provide curated public strategy names and descriptions for generated strategy templates.
- Reuse the existing redaction boundary so common-user payloads get safe product copy.
- Keep admin/internal payloads unchanged for audit and operation.
- Add focused tests proving common-user copy does not expose sensitive fields and admin copy remains technical.

**Non-Goals:**

- Change strategy parameters, template data, entry/exit rules, ranking, or backtest behavior.
- Add AI-generated copy.
- Add database schema or migration work.
- Remove existing admin/internal access to strategy secrets.

## Decisions

- Store public display names beside public descriptions in `strategy_descriptions.py`.
  - Rationale: names and descriptions are a product-copy catalog, not strategy execution data.
  - Alternative considered: rename `combo_templates.name` in the database. Rejected because template names are runtime identifiers used by execution and audit paths.
- Apply curated public names only inside the existing redaction layer.
  - Rationale: common-user surfaces already depend on `strategy_display_name`; admin payloads should keep raw technical identifiers.
  - Alternative considered: format names in frontend components. Rejected because Monitor, Favorites, exports, and future clients need the same visibility boundary.
- Keep unknown strategies conservative.
  - Rationale: unknown templates should get readable formatting when necessary, but descriptions must fall back to non-replicable generic copy if raw text looks technical.

## Risks / Trade-offs

- Public copy can become stale when new templates are added -> Mitigation: unknown-template fallback stays safe, and tests cover current generated templates.
- Names mention broad indicator categories such as momentum or volatility -> Mitigation: descriptions avoid parameter values, thresholds, formulas, and full entry/exit recipes.
- Existing database descriptions remain technical -> Mitigation: public payloads call the safe catalog; admin/internal surfaces may keep the raw database copy.
