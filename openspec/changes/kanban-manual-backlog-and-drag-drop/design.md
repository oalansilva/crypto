## Context

The current `/kanban` page is primarily a visualization and card-move surface for already existing workflow/OpenSpec changes. Alan wants to capture backlog items directly on the board, keep them visible in a **Pending** column, and let PO pull them into planning later. He also wants card movement to feel native on the board, especially drag-and-drop on desktop, with runtime workflow status updating automatically.

## Design Direction

Domain: kanban lane, intake tray, card handoff, workflow gate, pending backlog, move sheet
Color world: existing Kanban column surfaces, drag hover highlight, active drop target outline, subtle success refresh cue, muted secondary text for optional description
Signature: the board itself remains the primary control surface — create and move happen in-context instead of bouncing the user to separate planning screens
Rejecting: separate "new change" page -> inline/lightweight create flow, desktop-only move buttons -> direct manipulation drag/drop, divergent mobile logic -> same backend transition path with mobile-specific presentation
Direction: keep `/kanban` fast and operational. New work starts as a compact Pending card, desktop movement feels tactile via drag-and-drop, and mobile keeps a lower-risk action-sheet move flow that preserves the same workflow rules.

## Goals / Non-Goals

**Goals:**
- Add a Pending backlog stage before PO.
- Add a lightweight create-card flow directly inside `/kanban`.
- Add desktop drag-and-drop for moving cards between columns.
- Reuse a single backend transition path so desktop drag/drop and mobile move sheet stay consistent.
- Refresh the board immediately after create/move without requiring a full page reload.

**Non-Goals:**
- Full backlog grooming features (labels, priorities, assignees, rich forms).
- Replacing OpenSpec planning artifacts at PO stage.
- Implementing arbitrary workflow customization by end users.

## Decisions

1. **Represent Pending as a first-class runtime column/status before PO.**
   - Rationale: Alan explicitly wants backlog capture before PO planning. A dedicated runtime state is clearer than overloading `PO: not started`.
   - Alternative considered: keep PO as the first column and show unplanned cards there. Rejected because it blurs backlog intake with active PO work.

2. **Create cards through a dedicated backend Kanban/workflow endpoint.**
   - Rationale: the board needs a lightweight creation path that can persist runtime state immediately and later feed PO/OpenSpec work.
   - Alternative considered: create markdown/OpenSpec artifacts directly from frontend. Rejected because runtime DB/Kanban is the operational source of truth.

3. **Use a shared move API for desktop drag/drop and mobile stage picker.**
   - Rationale: one authoritative transition path reduces drift and keeps guard rails consistent.
   - Alternative considered: separate desktop and mobile move logic. Rejected because it doubles transition bugs.

4. **Keep auto-refresh query invalidation after successful mutations.**
   - Rationale: the user explicitly wants board status to update automatically after moves.
   - Alternative considered: optimistic-only local mutation. Rejected for v1 because backend validation/guard rails may reject some transitions.

## Risks / Trade-offs

- **[Pending cards exist before OpenSpec artifacts] → Mitigation:** treat runtime/Kanban as authoritative until PO pulls the card and creates planning artifacts.
- **[Drag/drop can feel fragile on mobile] → Mitigation:** scope drag/drop to desktop first and keep the current mobile move sheet.
- **[Status mapping bugs between columns and workflow gates] → Mitigation:** centralize mapping in backend and add route/tests for valid + invalid transitions.
- **[Create-card flow may need future metadata] → Mitigation:** start with title + optional description and keep payload extensible.

## Migration Plan

1. Add Pending to runtime/status derivation and board ordering.
2. Add backend create endpoint for Pending cards.
3. Add backend column/status transition mapping for board moves.
4. Add frontend create modal/inline form plus desktop drag/drop.
5. Add tests for create flow, move flow, and rejected transitions.
6. Deploy normally; rollback by hiding Pending/create/drag logic and reverting runtime mapping.

## Decision Details

### Pending card artifact policy

Newly created `Pending` cards are **runtime/Kanban-first** records. They MUST NOT require immediate OpenSpec folder creation at intake time. OpenSpec proposal/spec/tasks artifacts are created or updated when PO pulls the card from `Pending` into active planning.

**Why:** this preserves Kanban/workflow DB as the operational intake surface, keeps backlog capture lightweight, and avoids polluting OpenSpec with ideas that may never enter planning.

### Pending card description visibility

The optional short description MUST be stored in runtime and available in the card details view in v1. Showing it inline on the compact board card is optional and can remain a follow-up refinement if density becomes a concern.

## Key UX Flows

### Create-card flow

- The existing `New` affordance on `/kanban` opens a lightweight create flow anchored to the board context.
- Required input: title. Optional input: short description.
- On submit success, the new card appears in `Pending` without manual reload.
- Loading, validation, and error states stay inline/modal-local so the user never loses board context.

### Desktop drag-and-drop flow

- Dragging is enabled only on desktop/pointer layouts.
- Valid drop columns receive a clear hover/target state before release.
- On drop, the card keeps its place visually until the shared move mutation resolves, then the board refreshes from runtime.
- Invalid moves must fail with an actionable message rather than silently snapping back without explanation.

### Mobile move flow

- Mobile does not use drag-and-drop in v1.
- Tapping a move affordance opens the existing move sheet/action flow with the same allowed target stages as desktop.
- Confirmed mobile moves call the same backend transition path as desktop drag/drop and then refresh the board.
- This preserves parity of workflow rules while avoiding fragile touch drag behavior.
