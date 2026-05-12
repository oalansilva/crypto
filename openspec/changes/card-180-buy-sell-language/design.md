## Context

The Monitor currently uses internal trading-state names (`HOLD`, `EXIT`, `ENTRY`, `WAIT`) in several user-visible surfaces: KPI tags, section titles, row badges, card badges, chart current marker, signal history, E2E assertions, and product docs. The backend and resolver still need those raw states for technical classification and regression coverage.

## Goals / Non-Goals

**Goals:**
- Present visible Monitor decisions as `Compra` and `Venda` in the main list, detail card, and chart modal.
- Keep raw payload values such as `HOLDING`, `EXIT_SIGNAL`, `is_holding`, `entry`, and `exit` unchanged.
- Update tests and docs so public copy matches landing v3.
- Avoid wording that implies guaranteed profit or personalized financial advice.

**Non-Goals:**
- Changing backend strategy logic, stored status values, or API contracts.
- Renaming technical fields, enum values, logs, or internal test fixture statuses.
- Reintroducing visible `WAIT` as a third public signal.

## Decisions

- Centralize visible signal words in the Monitor signal resolver.
  Rationale: `resolveOpportunitySignal` already maps raw states to display visuals. Adding public label fields there keeps cards, list rows, and chart modal aligned without changing raw statuses.

- Preserve technical labels only where they identify internal payload or implementation state.
  Rationale: API payloads and existing regression fixtures rely on `HOLDING`, `EXIT_SIGNAL`, `entry`, and `exit`; renaming them would expand blast radius and risk backend regressions.

- Translate chart history labels to `Compra`/`Venda` while keeping marker direction and colors unchanged.
  Rationale: the user sees the same decision vocabulary, while the chart remains visually familiar.

- Update docs from `HOLD`/`EXIT` language to `Compra`/`Venda`.
  Rationale: product, landing, and app should share one public vocabulary.

## Risks / Trade-offs

- [Risk] Some raw backend messages may include `EXIT` in free text.
  Mitigation: translate the frontend surfaces controlled by Monitor components and keep backend message fields treated as technical context unless rendered as primary signal labels.

- [Risk] Tests still need raw internal states.
  Mitigation: fixture values remain raw; expectations for visible text change to `Compra`/`Venda`.
