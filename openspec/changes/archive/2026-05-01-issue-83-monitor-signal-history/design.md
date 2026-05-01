## Context

The chart modal already renders `Signal History` when `opportunity.signal_history` contains entries. The failing QA path tries to click `monitor-card-*`, but that element now lives inside a hidden detail row in the redesigned Monitor table.

## Goals / Non-Goals

**Goals:**

- Use the visible `monitor-row-*` workflow to open the chart modal.
- Keep validating that `Signal History` lists recent `ENTRY` and `EXIT` events.
- Keep marker-alignment copy covered by E2E.

**Non-Goals:**

- Redesign the Monitor table.
- Change signal history payload shape.
- Change marker rendering logic.

## Decisions

- Reuse the stable row selector added for the current Monitor table workflow.
- Keep assertions scoped to the modal history list and marker alignment text.
- Treat the old hidden-card selector as obsolete for this E2E scenario.

## Risks / Trade-offs

- The test now validates the active row action rather than the hidden expanded card.
- If the Monitor layout changes again, only the row-opening step should need updating.
