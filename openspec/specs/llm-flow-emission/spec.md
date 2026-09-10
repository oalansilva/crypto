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
Assessment A, Assessment B, `diff-reviewer`, and `code-reviewer` SHALL use the same model as the parent session and SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path. For Code Review, the parent SHALL attach the materialized interval (`review_diff_path:` and optional `## Diff` bytes) to the versioned agent file; the reviewer prompt MUST NOT instruct the child to fetch that interval with git or by listing transcripts.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B
- **THEN** each child uses the parent model
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer`
- **THEN** the prompt is the versioned agent file plus the parent-materialized interval
- **AND** it MUST NOT include the Design or Apply chat
- **AND** it MUST NOT ask the child to run git or list transcripts

### Requirement: Parent emits the review wave as two Tasks in one turn
When Code Review starts, the parent session's emitted tool call set for that turn SHALL include both `diff-reviewer` and `code-reviewer` Tasks. The parent MUST NOT emit the second reviewer only after destape or completion of the first. Operator-facing emission MAY note that host queueing is allowed and does not fail the card. Destape remains an order/poke (#879); its followup MUST NOT be emitted as permission to skip the pair or to birth the missing reviewer. This SHALL NOT add a state, event, hook, or `enabled_tools` change to `.cursor/process-fsm.yaml`.

#### Scenario: Same-turn wave is what the operator sees
- **WHEN** the parent starts Code Review after the interval is materialized
- **THEN** that parent turn contains two reviewer Task calls
- **AND** the chat does not show Apply→review→Apply→review as the happy path

#### Scenario: Destape of one reviewer does not birth the other
- **WHEN** destape fires because one reviewer already completed
- **THEN** the parent does not spawn the other reviewer in a later turn as a substitute for the wave
- **AND** if the pair has not returned, the parent waits
- **AND** destape matching, sidecar path, and poke≠`concluiu?` stay #879

### Requirement: Correction list and visible block are operator-facing
P1/P2 from both reviewers SHALL be emitted to the next Apply spawn as a single list in one prompt. After at most one correction Apply plus one wave, remaining P1/P2 SHALL be emitted as a visible block in the operator chat (not a third cycle, not a new column). An Apply child that returns early without a P0 SHALL produce the same class of visible block rather than a silent extra Apply. Done of this change is the next session not repeating Apply and review; extra automatic tests MUST NOT be published as the Done criterion.

#### Scenario: List not per-finding spawn
- **WHEN** the wave returns more than one P1/P2
- **THEN** the parent spawn prompt for correction contains the whole list
- **AND** the parent does not emit one Apply Task per finding

#### Scenario: Visible block after the correction ceiling
- **WHEN** P1/P2 remain after one correction Apply and one wave
- **THEN** the operator-facing message records the block
- **AND** no third Apply or third wave is spawned for those findings

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
The repository SHALL contain an operational token sheet at `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` for clone+delta chrome (shell width, CSS variables `--bg-*` / `--accent-primary`, Inter, real nav items, density). Human `DESIGN.md` and its visual YAML MUST remain intact and MUST NOT be rewritten by this sheet. The sheet is not the YAML of `DESIGN.md`. The sheet and chrome tokens MUST NOT replace a clone of the live page; Design MUST point at the live authenticated route (`/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, or another `/` catalog key) **or** at catalogued public HTML (`landing` = `https://criptofarol.com.br/`) when the surface already exists. Absence of the sheet file on disk MUST NOT authorize a gallery, BEFORE/AFTER panel, or chrome-only prototype.

#### Scenario: Clone+delta loads the sheet, not a DESIGN.md rewrite
- **WHEN** Design clones an existing product surface
- **THEN** the agent uses the token sheet plus the live/current screen as the visual base
- **AND** `DESIGN.md` is not overwritten
- **AND** the sheet does not claim to be the visual YAML

#### Scenario: Token sheet does not pass fidelity alone
- **WHEN** a prototype copies sidebar 224px and `--bg-*` from the token sheet but omits the live-route listing landmarks
- **THEN** fidelity MUST fail
- **AND** the missing token-sheet file MUST NOT be treated as permission to skip the route clone

#### Scenario: Public landing clone is not a token-sheet mock
- **WHEN** Design changes visible copy on the public landing
- **THEN** the canonical prototype is the cloned v4 page plus delta, not a token-sheet or ANTES/DEPOIS panel
- **AND** the token sheet MUST NOT replace catalog landmarks for key `landing`

### Requirement: Handoff comments record cost proxies
Design, Apply, and Review handoff comments SHALL record proxies: word count of `design.md`, bytes of prototype HTML generated versus copied, and number of spawns. They MUST NOT parse Cursor/Grok usage meters or add a dashboard.

#### Scenario: Design handoff includes proxies
- **WHEN** the Design comment is published on the card
- **THEN** it includes `design.md` word count, HTML generated-vs-copied bytes (or `N/A` when no prototype), and spawn count
- **AND** it does not include a parsed dollar amount from a vendor usage API

### Requirement: design.md declares parseable live_route or surface
For `UI impact: affected` with a prototype on disk, `design.md` MUST contain a parseable `live_route:` line and/or `surface: existing|new` as standalone fields (not prose-only, not only implied inside a narrative paragraph). Handoff proxies MAY still record copied-vs-generated bytes; those numbers MUST NOT replace the `COPIED:start`/`COPIED:end` sum used by T5.

#### Scenario: Prose-only route like #792 is refused
- **WHEN** `design.md` mentions `/monitor` only in prose and a prototype exists with `UI impact: affected`
- **THEN** T5 refuses
- **AND** the handoff proxy `copied vs generated` does not satisfy `G_design`

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

### Requirement: Stage child finishes in the host mode where it was spawned
Grill, Design-author, Apply, review, and QA children SHALL reach host `completed` in the Cursor host mode that spawned them (modo terminal on this VM, or modo Desktop+SSH Windows to this VM). The parent MUST NOT execute that stage on Desktop as a substitute for a dead or interrupted child. The operator MUST NOT resume an interrupted child as the passing child. Mixing modes to hide a host kill (grill on terminal, Apply finished by the parent on Desktop) MUST NOT count as the stage passing.

#### Scenario: Parent does not take over a dead Apply child on Desktop
- **WHEN** an Apply child on modo Desktop+SSH is interrupted by the host
- **THEN** the parent does not write product or harness patches for that stage in its own transcript
- **AND** the stage remains failed until a new child reaches `completed` in that same mode

#### Scenario: Operator resume of a corpse is refused
- **WHEN** the operator asks to continue an interrupted Task id as the successful Apply/review/QA child
- **THEN** the parent refuses that resume as acceptance
- **AND** it spawns a new isolated child with a self-contained prompt

