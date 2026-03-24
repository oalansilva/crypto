## Context

The current `home` spec still describes `/` as a lightweight navigation hub, but the actual product direction is already moving toward a richer first screen. The current `frontend/src/pages/HomePage.tsx` shows that evolution: hero copy, primary actions, a health/status block, summary KPIs, and contextual lists such as “Foco de hoje”.

This change exists to stop that evolution from remaining implicit. We need a design that formalizes the initial interface as a **daily cockpit** so DESIGN, DEV, and QA share the same information hierarchy and can distinguish between:
- stable layout expectations,
- lightweight status/snapshot content,
- and future dashboard ideas that should remain out of scope for now.

Constraints:
- Prefer existing frontend data and existing routes.
- Avoid introducing new backend/API requirements for this change.
- Keep the screen compact, readable, and responsive on desktop and mobile.
- Preserve fast access to core workflows; the cockpit must not become a slow, analytics-heavy dashboard.

Stakeholders:
- Alan (product direction and approval)
- DESIGN (hierarchy, copy, visual priority)
- DEV (implementation in `HomePage.tsx` and related UI primitives)
- QA (responsive validation and first-screen workflow coverage)

## Goals / Non-Goals

**Goals:**
- Define the Home page as a daily cockpit with a clear first-screen hierarchy.
- Preserve quick navigation while adding lightweight status, summary, and orientation blocks.
- Keep implementation incremental by building on the current Home structure instead of introducing a new frontend architecture.
- Make the page testable with deterministic sections, labels, and fallback states.

**Non-Goals:**
- Adding new backend endpoints or a new data aggregation service for Home.
- Turning Home into a full analytics dashboard with charts, drill-downs, or personalized recommendations.
- Reworking downstream pages such as Monitor, Lab, Combo, Kanban, or OpenSpec.
- Solving every “recent activity” or “portfolio intelligence” use case in this iteration.

## Decisions

1. **Home becomes a cockpit layered on top of the hub model**
   - Decision: `/` will remain the operational entry point for the product, but the layout will be structured as a cockpit: hero/orientation, primary actions, lightweight system status, summary cards, and contextual sections.
   - Rationale: this preserves the strength of the original hub concept while reflecting how the interface is already being used day-to-day.
   - Alternative considered: keep Home as a pure shortcuts page. Rejected because it underspecifies the richer first-screen experience the team is already building.

2. **Use existing frontend-accessible data and explicit fallback content**
   - Decision: the page should consume only data already available to the frontend in this iteration (for example, health/status checks) and use clearly-presented placeholder or static snapshot content where richer live data is not yet available.
   - Rationale: this avoids blocking the change on backend work and keeps the initial interface stable.
   - Alternative considered: require all KPI/status blocks to be fully live and data-driven. Rejected because it would expand scope and couple Home to new APIs.

3. **Three-layer information hierarchy**
   - Decision: the page will be organized into three visual layers:
     - top: orientation + primary next actions;
     - middle: compact summary/status cards;
     - bottom: contextual sections such as current focus, recent activity, or operational links.
   - Rationale: this keeps the “what should I do now?” answer above the fold while still providing useful context underneath.
   - Alternative considered: a uniform card grid with no hierarchy. Rejected because it makes all content compete equally and weakens first-action clarity.

4. **Primary actions are limited and task-oriented**
   - Decision: the hero area should emphasize a small number of high-frequency actions (for example: run a backtest, update data, open monitor), while secondary tools remain accessible in lower-priority sections.
   - Rationale: limiting the primary CTA set reduces clutter and reinforces a strong first decision.
   - Alternative considered: expose every major destination as a primary shortcut. Rejected because it recreates the old “all shortcuts are equal” problem.

5. **Responsive behavior favors stacking over compression**
   - Decision: on narrow screens, sections should collapse into a single-column flow with preserved tap targets and readable copy; avoid dense multi-column mini-dashboards that imply desktop-only usage.
   - Rationale: the cockpit must retain hierarchy on mobile instead of merely shrinking the desktop layout.
   - Alternative considered: preserve the same multi-panel composition across breakpoints. Rejected because it increases crowding and weakens readability.

6. **Frontend-only implementation with optional small component extraction**
   - Decision: implementation should stay in the existing Home page flow, extracting small presentational subcomponents only if it improves readability or reuse.
   - Rationale: this keeps the change low-risk and aligned with the current frontend architecture.
   - Alternative considered: introduce a dedicated dashboard module/state layer for Home. Rejected as unnecessary for the current scope.

## Risks / Trade-offs

- [Summary cards look “live” even when some values are placeholders] → Mitigation: use labels/copy that frame them as lightweight snapshots and keep status/error states explicit.
- [Too many sections reduce focus] → Mitigation: keep only a few primary actions above the fold and push secondary/navigation-heavy content lower in the layout.
- [Spec and implementation drift again] → Mitigation: the next `home` spec delta must describe the hierarchy and fallback behavior explicitly, not just list destinations.
- [Mobile layout loses hierarchy] → Mitigation: define responsive stacking rules around section priority, not just grid breakpoints.

## Migration Plan

- Update the `home` capability spec so it describes the cockpit behavior, including orientation, primary actions, summary/status blocks, and contextual sections.
- Align `frontend/src/pages/HomePage.tsx` with the approved hierarchy and ensure section names/copy match the spec.
- Validate desktop and mobile behavior, especially hero actions, status fallback states, and section ordering.
- No data migration is required.
- Rollback: revert Home to the simpler hub-oriented layout/spec if the richer cockpit proves too noisy or misleading.

## Open Questions

- Which summary cards should be treated as real data in this iteration versus explicitly static or illustrative content?
- Should Kanban/OpenSpec remain visible as operational shortcuts on the first screen, or move to a lower-priority “tools” grouping?
- Does Alan want one canonical “start here” path emphasized in the hero, or should the cockpit stay role-neutral?
