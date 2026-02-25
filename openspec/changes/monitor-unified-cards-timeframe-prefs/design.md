## Context

Monitor currently exposes overlapping views (Status/Dashboard) with the same filter scope and the same symbol universe. The project has evolved into a card-based mobile-first monitor, but the remaining tab structure adds UX friction.

Additionally, users want a per-symbol timeframe choice for Price mode, persisted in the backend to survive device changes.

Constraints:
- Preferences are per symbol (cards are per symbol).
- Stocks must remain 1d-only for now.
- Crypto supports intraday timeframes.

## Goals / Non-Goals

**Goals:**
- Unify Monitor into a single cards-based view (remove tabs).
- Keep In Portfolio vs All filter.
- Keep per-card Price vs Strategy toggle.
- Add per-card timeframe selector in Price mode.
- Persist `price_timeframe` in the backend, with defaults.

**Non-Goals:**
- Adding stock intraday support.
- Introducing user accounts/auth.
- Replacing the candle provider logic.

## Decisions

1) Remove Monitor tabs
- Decision: render a single monitor cards view and remove the Status/Dashboard tab switch.
- Rationale: reduces duplication and simplifies mental model.

2) Extend existing preferences model
- Decision: add `price_timeframe` to the existing `monitor_preferences` table and API.
- Rationale: avoids new tables/endpoints and keeps all per-symbol prefs together.

3) Backend validation
- Decision: backend validates `price_timeframe` values and enforces stocks=1d.
- Rationale: prevents invalid UI state and keeps behavior consistent across clients.

4) UI behavior
- Decision:
  - default filter: In Portfolio
  - symbols without preference appear only in All
  - default per-symbol timeframe: 1d
- Rationale: matches agreed UX and minimizes noise.

## Risks / Trade-offs

- [Risk] Removing tabs could confuse existing users → Mitigation: keep the core content available via per-card mode.
- [Risk] Preferences migration needed (new column) → Mitigation: SQLite `ALTER TABLE` at startup or create-if-not-exists; default values.
- [Risk] E2E selectors become unstable → Mitigation: use stable `data-testid` attributes.

## Migration Plan

1) Add backend column + API support.
2) Update frontend to remove tabs and add timeframe selector.
3) Update tests (integration + Playwright).
4) Deploy.

Rollback: revert to previous commit; column can remain unused.

## Open Questions

- Whether to expose timeframe selector for crypto only (or show disabled options for stocks). Current plan: show disabled for stocks.
