## Context

The /monitor dashboard currently computes entry distance incorrectly when trend up is false, causing misleading WAIT distances. Entry validity requires a crossover rule plus trend up (short > long), but distance measurement must adapt to trend state.

## Goals / Non-Goals

**Goals:**
- Apply the entry rule consistently: (crossover short/long OR short/medium) AND trend up.
- Use short→long distance when trend up is false.
- Use short→medium distance when trend up is true.

**Non-Goals:**
- Changing exit logic or hold (HOLD) distance calculations.
- Modifying UI layout or styling.

## Decisions

- **Single source of truth for entry-distance calculation**: implement the rule in the backend opportunity-monitor calculation path so both status and distance derive from the same logic.
  - *Alternative:* compute in the frontend. Rejected to avoid duplication and divergence from backend rule evaluation.
- **Trend gate first, then distance pair**: evaluate trend up (short > long) to choose which pair to measure, keeping the logic explicit and testable.

## Risks / Trade-offs

- **Risk:** Existing monitor rows may change ordering due to updated distance calculation. → **Mitigation:** Validate against known examples (e.g., screenshot case) and ensure rule matches stated entry logic.

## Migration Plan

- Deploy backend changes with existing stop/start scripts.
- No data migrations required.

## Open Questions

- Confirm whether distance measurement should be applied only to WAIT status (assumed) or also to any other non-hold states.
