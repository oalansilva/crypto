## Context

The workflow now includes a DESIGN stage (HTML/CSS prototypes) before Alan approval for UI changes. The Kanban board must represent this stage.

## Goals / Non-Goals

**Goals**
- Add DESIGN column to Kanban (always visible).
- Parse `DESIGN:` status from coordination files.
- Update derive-column rules: PO → DESIGN → Alan approval → DEV → QA → Alan homologation → Archived.

**Non-Goals**
- Making tasks checklist interactive.
- Implementing prototype generation itself (handled by the DESIGN agent).

## Decisions

- `DESIGN: skipped` is supported for non-UI changes.
- Column order is fixed and always includes DESIGN.

## Risks

- Coordination files that lack `DESIGN:` need a safe default. Default to `skipped` unless the change is explicitly marked UI-required (v1 simplest: default skipped).
