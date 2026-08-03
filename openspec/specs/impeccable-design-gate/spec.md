# impeccable-design-gate Specification

## Purpose

Define a reproducible Impeccable-assisted Design gate for Codex cards while preserving the Cripto Farol design system and the mandatory human approval step.

## Requirements

### Requirement: Codex Impeccable installation is project-local and reproducible
The project MUST provide a versioned project-local Impeccable installation for Codex, including the provider skill and its hook configuration, with the upstream version and resolved commit recorded in project documentation.

#### Scenario: Fresh checkout loads the same Codex skill
- **WHEN** an agent checks out the project and loads Codex skills
- **THEN** `.agents/skills/impeccable/` and `.codex/hooks.json` MUST be available from the repository
- **AND** the recorded Impeccable version and commit MUST identify the expected payload

#### Scenario: Hook installation preserves unrelated configuration
- **WHEN** the Impeccable hook is installed or updated
- **THEN** existing unrelated Codex hook entries MUST remain intact
- **AND** malformed or conflicting hook configuration MUST block installation rather than silently overwrite it

### Requirement: Product context MUST preserve the canonical Cripto Farol design system
The Impeccable context MUST identify the Cripto Farol product, audience, surface mode and anti-goals while treating the repository `DESIGN.md` as the canonical source for visual tokens and shell rules.

#### Scenario: Initialize context in the existing product
- **WHEN** the Impeccable context is initialized
- **THEN** a project product context MUST be available to later commands
- **AND** initialization MUST NOT overwrite or silently rewrite the existing `DESIGN.md`

#### Scenario: Existing surface is reviewed
- **WHEN** a card targets an existing screen or shell
- **THEN** the context and prototype MUST reference the current product surface as the base
- **AND** only the card delta MAY be introduced in the prototype

### Requirement: UI-impacting Design MUST run the structured Impeccable pipeline
For a Codex card marked `UI impact: affected`, the Design stage MUST run context loading, `shape`, a versioned prototype, independent `critique`, `audit`, applicable hardening commands, and final `polish` before requesting human design approval.

#### Scenario: Shape produces a confirmed design brief
- **WHEN** Design begins for a UI-impacting card
- **THEN** the card's `design.md` MUST record audience, outcome/proof, direction, scope, states, interaction/layout and constraints
- **AND** implementation of the prototype MUST not begin before material design ambiguity is resolved

#### Scenario: Findings determine specialized passes
- **WHEN** critique or audit identifies an error-state, device, copy, accessibility or overflow problem
- **THEN** the agent MUST run the applicable `harden`, `adapt`, `clarify` or equivalent targeted command
- **AND** the agent MUST NOT run unrelated visual commands merely to increase activity

### Requirement: Independent critics MUST inherit the primary Codex LLM
Assessment A and Assessment B MUST run in isolated read-only subagents using exactly the same LLM/model identifier and version as the primary Codex session.

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with subagent support available
- **THEN** Assessment A MUST review product/UX/heuristics and Assessment B MUST review detector/browser evidence in separate contexts
- **AND** both subagents MUST report the same primary-session LLM/model and version before synthesis

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot enforce or observe model equality or cannot provide the required subagent contexts
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no alternate model or silent degraded `PASS` MAY be used

### Requirement: Design evidence MUST be reproducible and gate PASS
The Design artifact MUST persist the Impeccable brief, critique, audit, trace, browser evidence, model metadata and version digest, and MUST allow `PASS` only when blocking findings and critical assertions are resolved.

#### Scenario: Successful UI Design handoff
- **WHEN** a UI-impacting prototype passes its final review
- **THEN** `design.md` MUST contain the Impeccable sections, `Prototype Validation`, `Design Critique` and an explicit `Design Agent verdict: PASS`
- **AND** the evidence MUST include desktop/mobile viewports, relevant interactions, asserts, console/page status and the validated digest

#### Scenario: Blocking finding remains
- **WHEN** a P0/P1 finding, critical detector finding, failed assert or relevant browser error remains unresolved
- **THEN** the verdict MUST be `BLOCKED`
- **AND** the card MUST remain in `Status=Design`

#### Scenario: Prototype changes after validation
- **WHEN** HTML/CSS/JS, build output or served prototype changes after browser validation
- **THEN** the previous validation evidence MUST be considered invalid
- **AND** the final browser gate MUST be executed again before PASS

### Requirement: Non-UI cards MUST retain the existing Design gate
Cards marked `UI impact: none` MUST continue through Design, Approval of Design and Alan's human approval, while documenting Impeccable as not applicable.

#### Scenario: Non-UI Design handoff
- **WHEN** a card has no new or changed visual surface
- **THEN** `design.md` MUST record `Prototype: N/A` and a non-empty justification
- **AND** the Design Critique MUST still cover scope, regressions, risks and the absence of visual change
