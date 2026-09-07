## ADDED Requirements

### Requirement: Critic classifies findings as product-blocking or Apply detail

The isolated Design critic SHALL classify each finding before verdict: only a visible product, scope, or contract problem (screen, states, accessibility, blown scope) MAY generate P0/P1. Implementation detail (ORM, internal names, polish) SHALL be recorded as P3 "detalhe de Apply", accepted in `design.md`, and resolved in Apply — the critic MUST NOT reopen it as P0/P1.

#### Scenario: Implementation detail becomes accepted P3

- **WHEN** the critic finds an implementation detail with no visible product/contract impact
- **THEN** it is published as P3 "detalhe de Apply" with disposition accepted
- **AND** the Design verdict is not blocked by it
- **AND** Apply resolves it without reopening Design

#### Scenario: Product problem still blocks

- **WHEN** the critic finds a visible product/scope/contract problem
- **THEN** it is published as P0/P1
- **AND** it counts toward the single rework under the round cap

### Requirement: Design closes within the round cap

A screen-less card SHALL close Design with at most 1 author + 1 critic + 1 rework; a card with screen keeps author + dual critic + 1 rework. A second rework SHALL occur only with a new product P0 justified in the prompt; otherwise the parent writes the critique section with the accepted P3s and submits. The author and critic prompts SHALL carry this cap verbatim (MUST Read, no fork).

#### Scenario: No new product P0 means submit with accepted P3s

- **WHEN** critique yields only P3 Apply details and no new product P0
- **THEN** the parent publishes the critique section with those P3s accepted
- **AND** no second rework is spawned

#### Scenario: Second rework needs a justified new product P0

- **WHEN** a second rework is proposed
- **THEN** the prompt justifies a new product P0
- **AND** without that justification the rework MUST NOT be spawned
