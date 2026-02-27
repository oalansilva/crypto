## Context

Home currently functions as a single feature promo (Combo Strategies), which is not aligned with how the product is used day-to-day (jumping between Monitor, Favorites, Lab, balances, and Kanban).

Constraint: keep this change small and iterative. In v1, Home is primarily a navigational hub; it should not require new backend work.

Stakeholders:
- Alan (approval + direction)
- DESIGN (prototype)
- DEV (implementation)

## Goals / Non-Goals

**Goals:**
- Provide a Home information architecture that clearly exposes the main workflows.
- Reduce clicks/time-to-action to get to common destinations.
- Enable a fast DEV implementation via a simple HTML/CSS prototype.

**Non-Goals:**
- Building personalized analytics (e.g., “recent runs”, “performance charts”) that require new endpoints.
- Changing the underlying features (Monitor, Lab, Combo, etc.).

## Decisions

1. **Home as a hub, not a dashboard (v1)**
   - Decision: Home will be mostly static UI + navigation shortcuts.
   - Rationale: fastest path to value; avoids dependency on backend data.
   - Alternative considered: show dynamic “recent activity” and status cards; rejected for v1 due to data/endpoint coupling.

2. **Prototype-first for consistent UI**
   - Decision: DESIGN will provide a reusable HTML/CSS prototype under `frontend/public/prototypes/home-page-refresh/`.
   - Rationale: improves speed and avoids UI drift across DEV iterations.

3. **Quick Actions as the primary interaction**
   - Decision: Quick Actions grid/cards is the primary Home interaction pattern.
   - Rationale: matches user intent (“take me to X”) and is simple to test.

## Risks / Trade-offs

- [Home feels too “static”] → Mitigation: keep copy concise and allow adding a small “What’s new” or “recent” block in a later iteration if needed.
- [Too many shortcuts creates clutter] → Mitigation: limit to core destinations listed in spec; keep consistent card style and short descriptions.

## Migration Plan

- Replace current Home content with the new hub layout.
- No data migration.
- Rollback: revert Home component to previous single-CTA version.

## Open Questions

- Should any shortcut be emphasized as the “primary” CTA (e.g., Monitor vs Combo) for Alan’s preferred daily workflow?
- Any destinations to hide for now (e.g., OpenSpec/Kanban) in a “Developer tools” subsection?
