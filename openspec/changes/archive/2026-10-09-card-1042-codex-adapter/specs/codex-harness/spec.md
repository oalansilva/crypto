## ADDED Requirements

### Requirement: Codex local sessions discover the canonical workflow
The fifth adapter SHALL work in Codex CLI and the local IDE extension from a trusted checkout. Each new session MUST discover repository skills, use canonical `.cursor/skills/` instructions through thin `.agents/skills/` bridges, and receive the `context_file` orientation for the bound card's current Status from the shared FSM. It SHALL use the existing OpenSpec CLI artifact workflow. The adapter MUST NOT copy the state table or runbook into `.codex/` or depend on Codex home skills as the active contract.

#### Scenario: Fresh CLI and IDE sessions
- **WHEN** a fresh CLI session and a fresh local IDE session start in the pinned card worktree
- **THEN** both can find `covenant-flow`, `design-critic`, and `openspec-*` skills from versioned project files
- **AND** both display the same bound card, `q_git`, enabled events, and `context_file[Status]` orientation from `.cursor/process-fsm.yaml`
- **AND** neither uses a copied FSM under `.codex/`

#### Scenario: Specification uses existing OpenSpec instructions
- **WHEN** the bound card is in Design and a Codex session creates OpenSpec artifacts
- **THEN** it uses `openspec instructions` and the canonical workflow skills
- **AND** it does not invent an artifact outside the active OpenSpec schema

#### Scenario: Unread Status does not become inferred permission
- **WHEN** the Status lookup is unavailable for a bound card
- **THEN** the orientation states `Status unread`
- **AND** product writing is denied rather than inferred from chat wording

### Requirement: Codex guards covered local writes at the card gate
The Codex adapter SHALL send supported local shell and file-edit tool calls through the shared `guard.decide()` before execution. A deny MUST prevent the target bytes from being written and expose the reason. Product writes on `develop` or while the bound card is in `Todo` MUST be denied by both command and file-edit routes. In Design, OpenSpec Design artifacts MUST remain writable in the bound worktree. Product writing SHALL be allowed only in the bound card worktree after T8 reaches `Em desenvolvimento`, subject to the existing FSM and Guard. Missing or invalid overlay MUST fail closed for product writes. Hook trust or uncovered routes MUST NOT be presented as universal enforcement or Auto mode.

#### Scenario: Develop command and edit are denied
- **WHEN** a trusted CLI or IDE session on `develop` attempts a product write through shell and through `apply_patch`
- **THEN** each covered operation is denied before mutation with a visible reason
- **AND** a readback proves the target bytes unchanged

#### Scenario: Todo command and edit are denied
- **WHEN** the bound card has `Status=Todo` and either surface attempts a product write through shell or file edit
- **THEN** the Guard denies both routes and the target remains unchanged

#### Scenario: Design artifacts pass while product remains gated
- **WHEN** the bound card has `Status=Design` in its card worktree
- **THEN** a write to its OpenSpec Design artifacts is allowed
- **AND** a product-path write is denied

#### Scenario: Legal product write follows T8
- **WHEN** `process_event iniciar_apply` has moved the approved card to `Em desenvolvimento` and the session is bound to its card worktree
- **THEN** the shared Guard allows a product-path fixture write permitted by the FSM
- **AND** the same write from `develop` remains denied

#### Scenario: Missing hook coverage is reported
- **WHEN** a tool route does not invoke the project `PreToolUse` hook or the hook is untrusted, disabled, or errors
- **THEN** the essay records the route and observed result as an enforcement gap
- **AND** docs and the board MUST NOT claim Codex Auto or complete interception

### Requirement: Codex resolves model and effort per band from one shared map
The adapter SHALL read `.cursor/model-map.yaml` before each Codex child request. `juizo.codex` SHALL select `gpt-6-sol` with effort `high`; `execucao.codex` SHALL select `gpt-6-luna` with effort `max`. A subsequent valid edit to either pair SHALL affect the next spawn of that band. At installation, top-level Cursor `juizo.label/slug`, `execucao.label/slug`, and all `forbid` entries SHALL be taken from the **current target consumer map** and preserved; the Codex adapter MUST NOT restore source or Design-worktree Cursor values. Missing, invalid, forbidden, or host-rejected model/effort MUST yield a visible failed spawn, without silent picker inheritance, default effort, alternate model, or retry fallback.

#### Scenario: Juízo and execução spawns use Alan's values
- **WHEN** a Codex parent requests one child from each band
- **THEN** the juízo spawn requests `gpt-6-sol` and `high`
- **AND** the execução spawn requests `gpt-6-luna` and `max`
- **AND** the observed child model and effort are recorded in the handoff proxy

#### Scenario: Map edit affects next spawn only
- **WHEN** a valid model or effort value for a band changes in the shared map
- **THEN** the next Codex spawn of that band requests the changed pair
- **AND** already running children keep their original pair
- **AND** Cursor spawns still use the unchanged Cursor values

#### Scenario: Target map conflict is not a successful pin
- **WHEN** the target consumer map has local top-level Cursor or `forbid` changes that differ from the product map
- **THEN** the pin reads and preserves the target fields while adding Codex subblocks
- **AND** any incompatible conflict is refused visibly or resolved through an explicit inspected merge
- **AND** the installer MUST NOT silently replace those fields

#### Scenario: Missing or unavailable pair refuses visibly
- **WHEN** the map lacks the required Codex model or effort, lists a forbidden value, or the host rejects either value
- **THEN** no child result is accepted for that request
- **AND** the operator sees the failed pair and reason
- **AND** no default, `inherit`, or alternate pair is used

### Requirement: Codex stage children are isolated and reviews use the exact diff
Design, Apply, Code Review, and QA SHALL run in isolated Codex children with self-contained activity prompts, no parent transcript, and the resolved band pair. The two Code Review children MUST receive the same parent-materialized exact diff, remain read-only, and return separate findings. The parent MUST NOT treat a missing or interrupted child as completed.

#### Scenario: Design and QA are separate children
- **WHEN** the parent enters Design or QA on the pilot card
- **THEN** it spawns the stage child with only the stage context and the selected pair
- **AND** the parent does not execute that stage's authoring or checks in its own transcript

#### Scenario: Two read-only reviewers inspect one interval
- **WHEN** Code Review begins with a materialized pre-commit or closing diff
- **THEN** `diff-reviewer` and `code-reviewer` receive the same exact interval and separate prompts
- **AND** neither modifies files nor fetches another diff from git
- **AND** their findings and completed status are recorded separately

#### Scenario: Incomplete child blocks stage success
- **WHEN** a child is interrupted, lacks a result, or runs under the wrong model or effort
- **THEN** that stage does not advance as a successful child execution

### Requirement: Codex advances Status only through the shared FSM
Codex agents SHALL call `process_event` for authorized transitions and MUST NOT edit the Project Status directly. Alan-only approvals remain human actions. A pilot card SHALL demonstrate Design, human approval, Apply, two reviews, QA, and Done técnico in order, with traceable event and child evidence.

#### Scenario: Pilot traverses all required gates
- **WHEN** the pilot card starts in `Todo`
- **THEN** its recorded trace includes `iniciar_design`, `submeter_design`, Alan's approval, `iniciar_apply`, two separate reviews, QA, and `integrar_develop`
- **AND** no product write occurs before T8 or without the bound worktree
- **AND** the terminal card state of this pilot is Done técnico, not an implied release

#### Scenario: Agent cannot substitute for Alan
- **WHEN** Codex receives chat wording asking to approve Design or homologate
- **THEN** it does not impersonate Alan or directly edit Status
- **AND** the human gate remains pending until Alan acts through the existing route
