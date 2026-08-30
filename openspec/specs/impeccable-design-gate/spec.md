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

### Requirement: Non-UI cards MUST retain the existing Design gate
Cards marked `UI impact: none` MUST continue through Design, Approval of Design and Alan's human approval, while documenting Impeccable as not applicable.

#### Scenario: Non-UI Design handoff
- **WHEN** a card has no new or changed visual surface
- **THEN** `design.md` MUST record `Prototype: N/A` and a non-empty justification
- **AND** the Design Critique MUST still cover scope, regressions, risks and the absence of visual change

### Requirement: Prototype clone+delta without HTML dump
For an existing product surface, the prototype MUST clone the live route page — listing, headers, actions, and expand, plus shell/nav/tokens/density — and apply only the card delta. Cloning only the current shell/nav/tokens/density is not sufficient. Design, critics, and operator chat MUST use the navigable URL, screenshot, and digest — they MUST NOT dump prototype HTML into chat or `design.md`. `/opsx:apply` MUST still read the prototype file on disk as the layout spec. Polish MUST patch the prototype file; it MUST NOT rewrite the whole HTML in the LLM. New surfaces still compose from the token sheet plus the authenticated app shell, not a generic landing; new surfaces are exempt from catalog/`copied` when `surface: new` or `live_route: N/A` is declared.

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

#### Scenario: Existing route clone includes listing landmarks
- **WHEN** Design clones an existing product surface such as `/monitor`
- **THEN** the prototype HTML contains the catalog landmarks for that route
- **AND** sidebar 224px plus `--bg-*` tokens alone MUST NOT pass fidelity

### Requirement: Existing-route prototype MUST clone live-route landmarks
For `UI impact: affected` when the surface already exists, the prototype MUST clone the authenticated live route page (listing, headers, actions, expand) and apply only the card delta inside that topology. Shell width 224px, `--bg-*` tokens, and the token sheet MUST NOT be treated as sufficient fidelity. Blocking fidelity is the versioned landmark catalog for that route.

#### Scenario: Monitor proto without listing landmarks is P0
- **WHEN** Assessment A or B reviews a `/monitor` prototype that has sidebar 224px and correct tokens but lacks `table.signals` or headers `Status` / `Preço` / `Risco até stop` / `Operar`
- **THEN** the verdict MUST be `BLOCKED` with a P0 fidelity finding
- **AND** chrome-only PASS is forbidden

#### Scenario: Delta stays inside the live topology
- **WHEN** a card changes a detail on an existing route
- **THEN** the prototype URL shows the same listing/actions landmarks as the live route
- **AND** the card delta is inside that topology, not a parallel layout

### Requirement: Gallery of states is P0 on list-plus-detail routes
When the live product is list-plus-detail, a prototype that renders N states as N cards in a grid MUST be a P0. Named anti-pattern: “N estados ⇒ N cards numa grelha”. This SHALL NOT treat a live template grid (Combo `/combo/select`) as that anti-pattern when the catalog landmarks for that route are present.

#### Scenario: Four-card gallery for Monitor is P0
- **WHEN** a `/monitor` prototype is a 2×2 gallery of state cards instead of `table.signals` plus row expand
- **THEN** Assessment MUST record P0
- **AND** T5 clone gate MUST classify that HTML as BLOCKED against `/monitor`

### Requirement: Dual critic opens the live route URL
When a session exists, Assessment A/B SHALL open the live DEV URL of the declared route and the prototype URL. A missing listing landmark on the prototype versus the live route is P0. Without a session, the critic MUST NOT treat `/login` as the live route. Authenticated Playwright MUST NOT run inside `submeter_design`.

#### Scenario: Login page is not the live route
- **WHEN** the critic has no session and the live URL redirects to `/login`
- **THEN** it MUST NOT treat login chrome as clone evidence
- **AND** it MUST NOT emit PASS on shell-only comparison to `/login`

#### Scenario: Session compares live listing to proto
- **WHEN** a session exists and `live_route` is `/monitor`
- **THEN** the critic opens the live `/monitor` URL and the prototype URL
- **AND** absence of a catalog listing landmark on the prototype is P0

### Requirement: Antes/Depois toggle MUST change the view
If the prototype exposes an Antes/Depois control, Antes MUST be the clone without the card delta and Depois MUST be clone+delta. A control that only flips `aria-pressed` without changing the view MUST be P0 when it is the only offered proof of clone. T5 SHALL NOT verify the toggle (offline static check).

#### Scenario: Dead toggle is P0
- **WHEN** the only clone evidence is an Antes/Depois button whose `aria-pressed` changes and the listing markup does not
- **THEN** Assessment MUST record P0
- **AND** T5 still uses landmarks and `copied`, not the toggle

