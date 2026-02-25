## Context

The Playground screen includes a primary action currently labeled “New Backtest”. The requested change is a copy-only rename to “New Backtest2”, without altering the underlying behavior.

Constraints:
- Keep the existing navigation/handlers unchanged.
- If the label is sourced from i18n/translation resources, update the correct key/value rather than hardcoding.

## Goals / Non-Goals

**Goals:**
- Update the visible label from “New Backtest” to “New Backtest2” on the Playground screen.
- Preserve existing click behavior and routing.

**Non-Goals:**
- No changes to backtest creation logic, API calls, or backend behavior.
- No redesign of the Playground UI.

## Decisions

- Prefer updating a single source of truth (i18n string or shared UI constant) to avoid drift.
- Keep tests minimal: assert rendered text and ensure existing action handler still triggers.

## Risks / Trade-offs

- [Risk] The string appears in multiple places (button label, tooltip, menu item) leading to partial rename → Mitigation: search for occurrences of “New Backtest” and verify UI locations.
- [Risk] i18n key is reused elsewhere, unintentionally renaming other screens → Mitigation: confirm usage sites of the key before changing; if shared, create a dedicated key for Playground.
