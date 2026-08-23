## MODIFIED Requirements

### Requirement: UI-impacting Design MUST run the structured Impeccable pipeline
For a Codex card marked `UI impact: affected`, the Design stage MUST run context loading, `shape`, a versioned prototype, independent `critique`, `audit`, applicable hardening commands, and final `polish` before requesting human design approval. The full shape brief MUST live in the `.impeccable/critique/` snapshot. `design.md` MUST record only a short recorte (audience, outcome, direction, scope) — not the integral Brief.

#### Scenario: Shape produces a confirmed design brief
- **WHEN** Design begins for a UI-impacting card
- **THEN** the snapshot MUST record audience, outcome/proof, direction, scope, states, interaction/layout and constraints
- **AND** `design.md` MUST record a short recorte of audience, outcome, direction and scope
- **AND** implementation of the prototype MUST not begin before material design ambiguity is resolved

#### Scenario: Findings determine specialized passes
- **WHEN** critique or audit identifies an error-state, device, copy, accessibility or overflow problem
- **THEN** the agent MUST run the applicable `harden`, `adapt`, `clarify` or equivalent targeted command
- **AND** the agent MUST NOT run unrelated visual commands merely to increase activity


### Requirement: Independent critics MUST inherit the primary Codex LLM
Assessment A and Assessment B MUST run in isolated subagents using exactly the same LLM/model identifier and version as the primary Design session. They MUST receive a self-contained prompt and MUST NOT inherit the parent transcript. They MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype files, or product code. Isolation is process (no shared transcript, instruction not to edit product), not a plugin.

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with subagent support available
- **THEN** Assessment A MUST review product/UX/heuristics and Assessment B MUST review detector/browser evidence in separate contexts
- **AND** both subagents MUST report the same primary-session LLM/model and version before synthesis
- **AND** neither spawn includes the parent Design transcript

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot enforce or observe model equality or cannot provide the required subagent contexts
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no alternate model or silent degraded `PASS` MAY be used

#### Scenario: Critic return is bullets plus snapshot
- **WHEN** Assessment A or B finishes
- **THEN** the return to the parent is P0–P3 bullets, disposition, verdict, and snapshot path
- **AND** the full rubric dump lives in `.impeccable/critique/`, not in the parent chat

### Requirement: Design evidence MUST be reproducible and gate PASS
The Design artifact MUST persist a short published verdict in `design.md` (bullets P0–P3, disposition, `Design Agent verdict`) and MUST persist the full Impeccable report, browser evidence, model metadata and version digest in a git-tracked `.impeccable/critique/` snapshot linked from the card. `PASS` is allowed only when blocking findings and critical assertions are resolved, the snapshot is non-empty, browser gate is green, and isolated same-model critique exists. Integral Brief/Critique/Audit/Trace MUST NOT appear in `design.md` or the operator chat. HTTP 200 isolated is never PASS evidence.

#### Scenario: Successful UI Design handoff
- **WHEN** a UI-impacting prototype passes its final review
- **THEN** `design.md` MUST contain UI impact, Prototype URL/digest, short `Impeccable` bullets, `Prototype Validation` summary, `Design Critique` bullets and an explicit `Design Agent verdict: PASS`
- **AND** the snapshot under `.impeccable/critique/` MUST contain the full rubric report
- **AND** the card comment MUST link that snapshot
- **AND** the evidence MUST include desktop/mobile viewports, relevant interactions, asserts, console/page status and the validated digest

#### Scenario: Blocking finding remains
- **WHEN** a P0/P1 finding, critical detector finding, failed assert, empty snapshot, or relevant browser error remains unresolved
- **THEN** the verdict MUST be `BLOCKED`
- **AND** the card MUST remain in `Status=Design`

#### Scenario: Prototype changes after validation
- **WHEN** HTML/CSS/JS, build output or served prototype changes after browser validation
- **THEN** the previous validation evidence MUST be considered invalid
- **AND** the final browser gate MUST be executed again before PASS

#### Scenario: Published design.md has no Nielsen table
- **WHEN** a reviewer inspects `design.md` after a UI-affected Design
- **THEN** it has no Nielsen heuristic table, no persona essay, and no integral Impeccable Brief/Critique/Audit/Trace
- **AND** those full sections exist only in the snapshot

## ADDED Requirements

### Requirement: Prototype clone+delta without HTML dump
For an existing product surface, the prototype MUST clone the current shell/nav/tokens/density and apply only the card delta. Design, critics, and operator chat MUST use the navigable URL, screenshot, and digest — they MUST NOT dump prototype HTML into chat or `design.md`. `/opsx:apply` MUST still read the prototype file on disk as the layout spec. Polish MUST patch the prototype file; it MUST NOT rewrite the whole HTML in the LLM. New surfaces still compose from the token sheet plus the authenticated app shell, not a generic landing.

#### Scenario: Critics review URL and digest
- **WHEN** Assessment A or B reviews a UI-affected prototype
- **THEN** the spawn context includes the HTTP URL, screenshot, and digest
- **AND** it does not include the prototype HTML source as chat payload

#### Scenario: Apply still reads the prototype file
- **WHEN** `/opsx:apply` implements a UI-affected card
- **THEN** it reads `frontend/public/prototypes/<change-or-card-slug>/` from disk as the layout spec
- **AND** it does not treat `design.md` bullets as a replacement for that file

#### Scenario: Polish is a patch
- **WHEN** targeted Impeccable fixes land on the prototype
- **THEN** the edit is a patch to the existing file
- **AND** the LLM MUST NOT emit a full-file HTML rewrite as the polish step
