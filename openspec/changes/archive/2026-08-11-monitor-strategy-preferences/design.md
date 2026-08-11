## Context

Monitor already computes opportunities from favorite strategy rows and renders strategy labels through `getStrategyDisplayName`. Non-admin redaction currently sets both `template_name` and `strategy_display_name` to `Estratégia protegida`, which protects internals but removes the public label users need for preference and learning.

Monitor also stores starred opportunities in `localStorage` under `crypto-monitor-favorites-v1`. This works per browser but does not model a user preference and can drift across devices.

## Decisions

1. Keep redaction strict, but make display names public.

   Common users may see a human-readable label derived from the strategy name, such as `multi_ma_crossover` -> `Multi MA Crossover`. They still cannot see raw `template_name`, `parameters`, `indicator_values`, `details`, or fallback admin `name`/`notes`.

2. Store liked Monitor strategies by user and favorite row ID.

   The opportunity ID is already the favorite strategy row ID. A new `monitor_strategy_preferences` table stores `(user_id, favorite_id, liked, updated_at)`. This keeps the smallest durable contract and avoids changing strategy execution, favorites ownership, or curated fallback selection.

3. Use the Monitor API for preference sync.

   Add:
   - `GET /api/monitor/strategy-preferences` -> `{ "<favorite_id>": { "liked": true } }`
   - `PUT /api/monitor/strategy-preferences/{favorite_id}` -> `{ "liked": boolean }`

4. Keep frontend fallback compatible.

   Monitor can still load legacy localStorage keys before API sync, then replace state from the backend when preferences load. Toggling the star updates state optimistically and persists through the API.

## Risks

- Public display names could leak too much if they include proprietary naming. Mitigation: expose a normalized display label only, not raw strategy code, parameters, or details.
- Curated fallback IDs belong to admin favorites. Mitigation: preference rows store only that the user liked a visible Monitor opportunity ID; they do not grant access to the source favorite record.
- API failure could make stars feel unreliable. Mitigation: optimistic update with rollback and toast on failure.

## Validation

- Unit/integration tests for redaction and Monitor strategy preference routes.
- Frontend build and affected Monitor E2E test.
- OpenSpec change validation.
