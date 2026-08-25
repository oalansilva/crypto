# llm-flow-emission Specification

## Purpose
Contrato transversal de **emissão** (chat/`design.md`/handoff) vs **avaliação** Impeccable. Snapshot, um chat por card + filhos de atividade, contexto fatiado no apply, folha de tokens, proxies de custo. Não enfraquece gates.

## Requirements

### Requirement: Evaluation stays full; critique emission is bullets
The Design/Apply/Review flow SHALL keep the full Impeccable **avaliação** (rubrica, shape, dual critic, detector, browser, zero P0/P1) and SHALL cap **emissão da crítica** in the operator-facing chat and in the Impeccable/Design Critique sections of `design.md`. That published critique MUST be bullets P0–P3 with disposition and a verdict. Extra findings MUST become extra bullets (no hard line cap). Chat and `design.md` MUST NOT contain a Nielsen table, a persona essay, or integral Impeccable Brief/Critique/Audit/Trace. Truncating a finding to meet a line budget is forbidden. `design.md` MAY still hold short OpenSpec sections that apply rereads: problem, decisions, `## Apply contract`, UI impact, and prototype URL/digest.

#### Scenario: UI-affected Design publishes a short critique
- **WHEN** Design finishes for a card with `UI impact: affected`
- **THEN** the parent chat and the Impeccable/Design Critique sections of `design.md` show only P0–P3 bullets, disposition, and verdict
- **AND** they do not include a Nielsen table, persona essay, or full Impeccable Brief/Critique/Audit/Trace
- **AND** `design.md` still contains the short apply sections (problem, decisions, Apply contract, UI impact, prototype URL/digest)

#### Scenario: Extra findings become extra bullets
- **WHEN** the isolated critique produces more findings than a short list
- **THEN** each finding is still published as a bullet
- **AND** no finding is dropped or truncated to satisfy a line count

### Requirement: Snapshot holds the long report and is not apply/review input
The complete critique report SHALL be written under `.impeccable/critique/` and SHALL remain git-tracked. The OpenSpec Gist MUST NOT upload that folder. The card comment MUST link the snapshot path so Alan can open it at T7. `/opsx:apply` and Code Review MUST NOT read the snapshot as implementation or review context. An empty or missing snapshot on a UI-affected card MUST keep the Design verdict `BLOCKED`.

#### Scenario: Snapshot linked, not inlined
- **WHEN** a UI-affected Design handoff is published
- **THEN** `.impeccable/critique/` contains a non-empty snapshot for that card/change
- **AND** the card comment includes a link or repo path to that file
- **AND** the Gist files are only OpenSpec Markdown (proposal/design/specs/tasks)

#### Scenario: Empty snapshot blocks PASS
- **WHEN** Assessment A/B ran but `.impeccable/critique/` has no snapshot body for the card
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** the card MUST remain in `Status=Design`

#### Scenario: Apply and review skip the snapshot
- **WHEN** `/opsx:apply` or Code Review starts
- **THEN** the agent MUST NOT load `.impeccable/critique/` as a context file
- **AND** MUST follow `design.md` short sections, specs, tasks, and the prototype file when UI-affected

### Requirement: Critics inherit model, not transcript
Assessment A, Assessment B, `diff-reviewer`, and `code-reviewer` SHALL use the same model as the parent session and SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B
- **THEN** each child uses the parent model
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer`
- **THEN** the prompt is the versioned agent file plus the diff under review
- **AND** it MUST NOT include the Design or Apply chat

### Requirement: One chat per column without a new FSM gate
The runbook SHALL require one operator chat per card titled `#<id>` covering Em Refinamento through Done técnico on both Cursor and Grok. Homologado and Release/lote MUST stay out of that chat. The parent session MUST NOT execute grill, Design authorship (except writing only `## Design Critique` after A/B as specified in `cursor-harness`), Apply, Code Review, or QA; it SHALL spawn an isolated child (or dual-critic / dual-reviewer wave) whose prompt is only that activity's context. Mixing activities means the parent executing another column, not a missing chat title. When Apply is requested without `Status=Pronto para Dev`, the parent MUST refuse in the **same** chat with current Status plus “Apply só depois de Pronto para Dev (T7 teu)” and MUST NOT ask the operator to open `#<id> Apply`. This SHALL NOT add a state, event, hook, or `enabled_tools` change to `.cursor/process-fsm.yaml`.

#### Scenario: Agent refuses a mixed column chat
- **WHEN** a chat `#<id>` is in `Status=Design` and receives an Apply/Review/Release execution request
- **THEN** the parent refuses to execute that other activity itself
- **AND** it does not tell the operator to open a new chat titled `#<id> <coluna>`
- **AND** if Status is not `Pronto para Dev`, it does not spawn the Apply child
- **AND** `process-fsm.yaml` is unchanged

#### Scenario: New column starts a new chat
- **WHEN** the operator starts Apply after Design in the same `#<id>` chat and `Status=Pronto para Dev`
- **THEN** Apply runs in an isolated child spawned from that same chat
- **AND** the parent does not continue executing Apply in its own transcript
- **AND** the operator is not told to open `#<id> Apply`

### Requirement: Apply context is sliced
For each apply task, the agent SHALL load that task, the spec file(s) of the capability the task implements, and the short apply sections of `design.md` (`## Apply contract`, prototype URL/digest when UI-affected, UI impact). It MUST NOT load the whole OpenSpec package, the Impeccable snapshot, or a dumped prototype HTML as chat context. The approved prototype file on disk remains the layout spec (#530).

#### Scenario: Task start does not ingest the whole change
- **WHEN** an apply task begins
- **THEN** the loaded context is the current task, the matching capability spec, and the short `design.md` apply sections
- **AND** the agent does not read every `contextFiles` path as a single dump
- **AND** it does not read `.impeccable/critique/`

### Requirement: Agent token sheet does not replace DESIGN.md
The repository SHALL contain an operational token sheet at `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` for clone+delta (shell width, CSS variables `--bg-*` / `--accent-primary`, Inter, real nav items, density). Human `DESIGN.md` and its visual YAML MUST remain intact and MUST NOT be rewritten by this sheet. The sheet is not the YAML of `DESIGN.md`.

#### Scenario: Clone+delta loads the sheet, not a DESIGN.md rewrite
- **WHEN** Design clones an existing product surface
- **THEN** the agent uses the token sheet plus the live/current screen as the visual base
- **AND** `DESIGN.md` is not overwritten
- **AND** the sheet does not claim to be the visual YAML

### Requirement: Handoff comments record cost proxies
Design, Apply, and Review handoff comments SHALL record proxies: word count of `design.md`, bytes of prototype HTML generated versus copied, and number of spawns. They MUST NOT parse Cursor/Grok usage meters or add a dashboard.

#### Scenario: Design handoff includes proxies
- **WHEN** the Design comment is published on the card
- **THEN** it includes `design.md` word count, HTML generated-vs-copied bytes (or `N/A` when no prototype), and spawn count
- **AND** it does not include a parsed dollar amount from a vendor usage API
