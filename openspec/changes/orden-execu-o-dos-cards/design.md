# Design — orden-execu-o-dos-cards

## Goal

Define the minimum safe UX for manual card reordering inside a single Kanban column so the visible order becomes the operational pull order for agents.

## Design principles

- Keep the interaction explicit and low-risk.
- Reorder must work without changing workflow stage/column.
- The first version should optimize clarity over flexibility.
- Mobile must remain usable even if the interaction differs from desktop.

## Interaction model

### Desktop

Use lightweight inline controls on each card:
- **Move up**
- **Move down**

Behavior:
- controls are visible on hover/focus and available in the card detail drawer as a fallback
- clicking a control reorders the card by one position within the same column
- the board updates immediately after success
- the moved card gets a brief visual highlight so the user understands what changed

Why this approach:
- lower implementation and QA complexity than drag-and-drop ordering
- easier to keep deterministic and accessible
- clearer auditability for the first release

### Mobile

Use the same semantic actions in a mobile-friendly form:
- expose **Move up** / **Move down** in the card actions area or detail drawer
- avoid relying on drag gestures for the first version

Why this approach:
- consistent behavior across devices
- lower risk than gesture-heavy reorder for the initial release

## UX states

### Success
- board re-renders in the new order immediately
- moved card remains visible in its new position
- optional small success toast: `Order updated`

### Error
- if persistence fails, keep the previous visual order
- show a short inline/toast error: `Could not update order`
- do not leave the UI in a speculative inconsistent state

### Boundary behavior
- first card cannot move up
- last card cannot move down
- controls should be disabled in those boundary states

## Data/behavior constraints

- reorder is allowed **only within the current column**
- reorder must not change approvals/gates/status
- the persisted order must be stable on refresh
- board queries must return cards already sorted in the saved order

## Operational rule

Within a given column, agents should pull work in the visible top-to-bottom order.

## Acceptance-oriented design checks

- user can move a middle card up by one position
- user can move a middle card down by one position
- refresh preserves the saved order
- mobile user can reorder through explicit actions without drag-and-drop
- no action allows crossing columns or bypassing workflow gates
