## Context

The Monitor screen was redesigned around a compact row/table layout. The older QA test still looked for the hidden expanded `OpportunityCard`, so it failed before opening the chart modal. The visible workflow now starts from the Monitor row and its chart action.

## Goals / Non-Goals

**Goals:**

- Keep the current Monitor row/table layout.
- Make the visible Monitor row addressable by test id.
- Make the chart modal's signal context block addressable and verify that it shows the resolved state.
- Preserve the existing signal-resolution logic.

**Non-Goals:**

- Redesign Monitor cards or restore the old mobile-only card list.
- Change backend opportunity payloads.
- Change HOLD/WAIT/EXIT resolution rules.

## Decisions

- Add stable test ids to the visible row and modal signal context instead of coupling QA to a hidden detail card.
- Keep the modal copy unchanged: `Resolved state`, strategy timeframe, displayed timeframe, reference candle, latest displayed candle, and status/freshness explanation.
- Update the E2E path for #82 to open the modal through the visible chart button.

## Risks / Trade-offs

- Existing tests that still target hidden detail cards may need separate follow-up alignment.
- The fix validates current UX rather than reviving older card-click behavior.
