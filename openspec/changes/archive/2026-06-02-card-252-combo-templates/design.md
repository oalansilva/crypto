## Context

The Combo selection page fetches `GET /api/combos/templates` and renders the total from the returned `prebuilt`, `examples`, and `custom` arrays. The endpoint delegates to `ComboService.list_templates()`, which reads `combo_templates` through the configured runtime database session.

Card #252 reports the UI showing `0 strategies stored in database` while recent operational state expects saved combo templates/favorites to exist. Runtime validation must use PostgreSQL, not SQLite, and the UI should keep the existing compact template-grid behavior aligned with `DESIGN.md` tokens for icon buttons, modest type scale, and stable grid cards.

## Goals / Non-Goals

**Goals:**

- Make `/api/combos/templates` return runtime PostgreSQL combo templates whenever valid rows exist.
- Repopulate the runtime template table from the versioned export when it is empty, using the existing startup seed logic.
- Keep the existing response shape consumed by `ComboSelectPage`.
- Add focused regression coverage for non-empty runtime template lists.
- Validate database count, API response, and served Combo UI/DOM.

**Non-Goals:**

- Redesign the Combo screen.
- Change template creation, backtest, optimization, or favorite-save semantics.
- Introduce SQLite as an operational fallback.
- Restore custom templates that are not present in the versioned export.

## Decisions

- Keep the UI endpoint unchanged. The page already calls `/api/combos/templates`, which is the documented database-driven endpoint; changing the frontend route would add churn without solving a backend/runtime listing defect.
- Fix listing at the service/query boundary. The endpoint should be a thin wrapper and keep Pydantic response validation.
- Reuse the existing `seed_combo_templates_if_empty()` startup helper when the runtime listing is empty. This keeps the seed source centralized and avoids a second import path or SQLite fallback.
- Preserve the three response buckets. `prebuilt`, `examples`, and `custom` are part of the current UI contract and existing specs.
- Treat invalid/malformed template rows defensively only if discovered during implementation. Valid rows must be returned with `name`, `description`, and `is_readonly`; malformed rows should not make the whole list appear empty unless they truly break the database query.

## Risks / Trade-offs

- Runtime DB has zero `combo_templates` rows -> the code restores the versioned baseline templates, but cannot recover custom templates that were never exported.
- Auth may gate the endpoint in browser/API validation -> use an authenticated runtime path or documented local override for evidence.
- Existing uncommitted work in the main worktree -> keep all card #252 changes isolated in the `card-252-combo-templates` worktree.
