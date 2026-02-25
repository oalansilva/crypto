## Context

The /lab page currently displays the title “Strategy Lab” in the header. The product naming has shifted to “Agent Trader,” so the UI copy needs to be updated to match the new branding. This is a small, frontend-only change.

## Goals / Non-Goals

**Goals:**
- Update the visible /lab page header title to “Agent Trader”.
- Keep the change localized to the UI with no backend impact.

**Non-Goals:**
- Renaming routes, APIs, or backend concepts.
- Changing any business logic or Lab workflow.

## Decisions

- **Update the Lab header string in the frontend** where the /lab page title is rendered.
  - *Rationale:* The requirement is purely presentational. A direct UI string update is the lowest-risk and most maintainable option.
  - *Alternative considered:* Introducing a configurable title in backend settings, rejected as unnecessary for a single-label change.

## Risks / Trade-offs

- **Risk:** The title may be rendered in multiple components or reused in other places.
  - **Mitigation:** Search the frontend for “Strategy Lab” and update only the /lab header usage.

## Migration Plan

- Deploy as part of the normal frontend release. No data migration needed.
- Rollback by reverting the string change if needed.

## Open Questions

- None.
