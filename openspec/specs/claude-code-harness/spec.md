# claude-code-harness Specification

## Purpose
TBD - created by archiving change card-1101-claude-code-adapter. Update Purpose after archive.
## Requirements
### Requirement: Claude Code sessions discover the canonical workflow
The `claude` adapter SHALL make a fresh Claude Code session in the repository load `AGENTS.md` through a root `CLAUDE.md` bridge that only imports it, discover repository skills through `.claude/skills/<name>/SKILL.md` bridges that point to the canonical `.cursor/skills/<name>/SKILL.md`, and receive the Moore page for the bound card's current Status from the shared `paging.page()`. Bridges MUST NOT copy the FSM, the runbook, skill bodies or the model policy, and SHALL be verified against a hash manifest. The adapter SHALL use the existing OpenSpec CLI workflow without inventing artifacts.

#### Scenario: Fresh session finds skills and Status orientation
- **WHEN** a new Claude Code session starts in a pinned card worktree
- **THEN** `covenant-flow`, `grill-card`, `design-critic` and `openspec-*` are discoverable from versioned `.claude/skills/` bridges
- **AND** the session context shows `q`, `bound_card`, `q_git`, `enabled_events` and the `context_file[Status]` orientation from `.cursor/process-fsm.yaml`
- **AND** no copy of the FSM, runbook or policy exists under `.claude/`

#### Scenario: Bridge drift is refused
- **WHEN** a `.claude/skills/` bridge differs from its manifest hash or contains workflow text
- **THEN** the installer and the bridge check fail visibly without overwriting the local file

#### Scenario: Unread Status is not permission
- **WHEN** the Status lookup fails at session start
- **THEN** the page states `Status unread` and product writing stays denied

### Requirement: Claude Code guards product writes by Status and binding
Supported Claude Code shell and file-edit tool calls (`Bash`, `Edit`, `Write`, `NotebookEdit`, and `MultiEdit` where the host has it) SHALL pass through the shared `guard.decide()` in a `PreToolUse` hook before execution. A deny MUST prevent mutation and show the reason. Product writes (overlay `product_globs`) on the integration branch, while the bound card is in `Todo`, or with no bound card MUST be denied by both command and file-edit routes. In Design, the Design artifacts (overlay `design_globs`) in the bound worktree MUST remain writable. Product writing SHALL be allowed only in the bound `card-<id>-*` worktree after T8. Hook errors, timeouts and invalid input MUST result in deny, never in a non-blocking error.

#### Scenario: Integration branch command and edit denied
- **WHEN** a session on `develop` attempts a product write via `Bash` and via `Edit`
- **THEN** both are denied before mutation with a visible reason and a readback shows the bytes unchanged

#### Scenario: Todo and unbound writes denied
- **WHEN** the bound card is in `Todo`, or no card is bound, and a product write is attempted by command or edit
- **THEN** both routes are denied and the target is unchanged

#### Scenario: Design artifacts allowed, product denied
- **WHEN** the bound card is in `Design` in its worktree
- **THEN** a write under `openspec/changes/**` is allowed and a write under `backend/**` is denied

#### Scenario: Product write after T8
- **WHEN** `iniciar_apply` moved the approved card to `Em desenvolvimento` and the session is in its worktree
- **THEN** the Guard allows the product write permitted by the FSM, and the same write from `develop` stays denied

#### Scenario: Implement request in Todo
- **WHEN** Alan asks `implemente` in Claude Code for a card in `Todo`
- **THEN** no product file changes
- **AND** the reply cites the current Status and that Apply only comes after Pronto para Dev

#### Scenario: Failing hook blocks
- **WHEN** the adapter raises, times out or receives malformed input on `PreToolUse`
- **THEN** the tool call is denied visibly

### Requirement: Stage children are isolated Claude Code subagents
Grill, Design author and critic, Assessment A/B, Apply, the two reviewers, QA and `fecho-lote` SHALL run as Claude Code subagents spawned by the parent session with a self-contained prompt (card, Status, worktree, authorized action, scope, canonical skill, output contract) and no parent transcript. Subagents MUST NOT spawn subagents. `diff-reviewer` and `code-reviewer` SHALL be defined in `.claude/agents/` with read-only tools only and no pinned model or effort; they SHALL be spawned in the same parent message, receive the same parent-materialized diff path and SHA-256, and return separate findings. A missing, interrupted or payload-less child MUST NOT count as completed.

#### Scenario: Review wave in one turn
- **WHEN** Code Review starts with a materialized diff
- **THEN** both reviewers are spawned in the same parent message with the same diff path and digest and separate prompts
- **AND** neither uses a tool other than `Read`, `Grep` or `Glob`
- **AND** `verify-wave` passes only with two distinct completed children with payload and matching observed pairs

#### Scenario: Child cannot spawn
- **WHEN** a subagent attempts the `Agent` tool
- **THEN** the `PreToolUse` hook denies it visibly

#### Scenario: Grill relaying keeps all options
- **WHEN** the `grill-card` child returns a closed question with its options
- **THEN** the parent relays it to Alan with every option the child listed, without collapsing to the recommended one
- **AND** the grill child writes the issue body

### Requirement: Claude Code children use the band selection with explicit model and effort
Before each spawn the parent SHALL run `model_selection.py resolve --client claude --band <band> --role <role> --capture <path>` and pass the resolved native `model` and `effort` arguments to the `Agent` tool, citing the capture in the prompt. `juizo.claude` SHALL be `claude-opus-5-5` with effort `high` and `execucao.claude` SHALL be `claude-sonnet-5-5` with effort `high` in the operator's local selection. A local edit SHALL affect the next spawn of that band only, without changing other clients. A missing, forbidden, unsupported or unavailable model or effort, a host without per-invocation effort, or an environment override of subagent model or effort MUST fail visibly before or at spawn, with no omission, inheritance from the parent, or substitution. A runtime-resolved model different from the captured model MUST invalidate that child. Every spawn SHALL carry explicit `model` and `effort`, because the host runs a child without explicit effort at its default effort. The spawn hook SHALL read the requested effort only from the `Agent` call's `tool_input.effort`, never from the session-level effort field of the hook input or the environment; if a host version does not expose that field, the spawn MUST be denied as `unsupported_schema` for that version and MUST NOT be accepted on `model` alone. Before a child's first file edit or write command, the adapter SHALL compare the latest model and effort in that child's transcript with the birth capture and MUST deny the write and mark the receipt `model_mismatch` when they diverge or cannot be read. Per-turn effort checks at collection SHALL remain.

#### Scenario: Bands use Alan's values
- **WHEN** the parent spawns one juízo and one execução child
- **THEN** the juízo spawn requests Opus 5.5 with effort high and the execução spawn requests Sonnet 5.5 with effort high
- **AND** the observed model and effort of each child are recorded

#### Scenario: Unavailable band model stops the stage
- **WHEN** the band model is absent, forbidden or unavailable when the parent tries to open the child
- **THEN** the stage stops with a visible error and no child result is accepted

#### Scenario: Spawn without explicit pair is denied
- **WHEN** an `Agent` call lacks the captured `model` or `effort`, or `CLAUDE_CODE_SUBAGENT_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` or `CLAUDE_CODE_EFFORT_LEVEL` is set
- **THEN** the hook denies the spawn visibly

#### Scenario: Resolved model diverges
- **WHEN** the host resolves the spawn to a model different from the captured id
- **THEN** the child is marked invalid and a new birth with the current selection is required

#### Scenario: Effort only from the Agent call
- **WHEN** an `Agent` call has no `tool_input.effort` but the hook input carries a session-level effort equal to the capture
- **THEN** the spawn is denied visibly as `unsupported_schema` for that host version
- **AND** no spawn is accepted on `model` alone

#### Scenario: Child model checked before its first write
- **WHEN** a child's first `Edit`, `Write` or write `Bash` call arrives and the latest `message.model` or `effort` in its transcript differs from the capture, or the transcript cannot be read
- **THEN** the write is denied before mutation and the birth receipt is marked `model_mismatch`
- **AND** a new birth is required

### Requirement: Claude Code runtime evidence is collected and gates on absence
The adapter SHALL prepare a birth receipt before each spawn and collect, after return, the observed model and effort, child identity, parent linkage, status, returned payload, host version and surface from the local Claude Code session and subagent transcripts, sealed with digests and kept separate from the requested capture. Evidence SHALL be accepted for any host version whose records match the `claude-transcript-v1` schema, as defined by `host-version-acceptance`; the observed host version SHALL be recorded and MUST NOT by itself refuse the evidence. Missing, divergent, truncated or foreign evidence MUST be `unavailable` or refused and MUST fail every gate that requires it; configuration or the child's own claim MUST NOT stand in for observation. A host-generated error turn (`<synthetic>` model) that ends the child SHALL classify the attempt as `failed`, never as `model_mismatch` and never as success. Identity checks between a child and its parent SHALL use the parent's cwd and host version recorded in the birth receipt, so a child born before the session switched worktree stays collectable. The birth receipt SHALL bind the card named in the task name when the session is on the integration branch or otherwise unbound (grill), and MUST refuse visibly when a bound card differs from the task-name card.

#### Scenario: Completed child with matching evidence
- **WHEN** a child returns completed with payload and the transcript shows the captured model and effort on every turn
- **THEN** the proxy records client `claude`, requested and observed pairs, status and payload without manual input

#### Scenario: Missing evidence fails the gate
- **WHEN** the transcript is missing, truncated, no longer matches the expected schema or belongs to another child
- **THEN** the observation is `unavailable` or `unsupported_schema` and the dependent gate is refused visibly while artifacts are preserved

#### Scenario: API error turn is a failed child
- **WHEN** the child's last assistant record is a host-generated `<synthetic>` error turn (for example after HTTP 429)
- **THEN** the proxy records the attempt as `failed` without success, and a new birth is required
- **AND** the collector does not report `model_mismatch` for that turn

#### Scenario: Child born before a worktree switch
- **WHEN** a child was born while the session was in one worktree and the session moved to another worktree before collection
- **THEN** collection compares the child's cwd and version with the parent values in the birth receipt and succeeds when they match

#### Scenario: Grill outside a card worktree records the requested card
- **WHEN** a `grill-card <id>` child is prepared in a session on the integration branch
- **THEN** the receipt and proxy record card `<id>` from the task name
- **AND** a session bound by git to a different card refuses the preparation visibly

### Requirement: Claude Code advances Status only through the shared FSM
Claude Code sessions SHALL change Status only through `process_event --client claude` with events enabled by the FSM. The client SHALL be detected natively and conflicting client identity SHALL be refused. Transitions that depend on children SHALL require a passing Claude Code evidence preflight, including active, trusted hooks. Human gates T1, T7, T15 and T18 MUST remain Alan's; chat wording such as `implemente` MUST NOT authorize code outside Pronto para Dev. No state, event, edge or human gate SHALL be added or changed.

#### Scenario: Apply through Done técnico in Claude Code
- **WHEN** a card in Pronto para Dev continues in Claude Code
- **THEN** `iniciar_apply`, Apply, `pedir_review`, two reviews, `aceitar_sha`, QA and `integrar_develop` occur with the expected children and events
- **AND** the handoff records the client and observed model of each child

#### Scenario: Agent cannot cross a human gate
- **WHEN** chat asks the Claude Code agent to approve Design or homologate
- **THEN** `process_event` rejects the human event and Status is unchanged

#### Scenario: Missing hooks surface at the transition
- **WHEN** hooks are disabled, untrusted or absent in the session
- **THEN** the dependent `process_event` is rejected with a visible Claude Code evidence reason

### Requirement: Cards may switch client between stages
A card SHALL be able to run different stages in different clients under the same FSM. Each child's capture, proxy and handoff SHALL record the client and observed model actually used, and later handoffs SHALL show those of earlier stages. No child SHALL be transferred to another client as fallback.

#### Scenario: Design in Cursor, Apply in Claude Code
- **WHEN** a card's Design ran in Cursor and its Apply continues in Claude Code
- **THEN** Status advances by the same events
- **AND** the handoff shows client and model of each child, including those of the Design stage

### Requirement: Claude Code conducts the agent part of batch closeout
Batch closeout in Claude Code SHALL start only on Alan's explicit request and follow the same rules as other clients: the parent session's observed model and effort MUST match the captured `claude/execucao` selection, otherwise T16 and `fecho-lote` are refused and a new session is required; one isolated `fecho-lote` child runs with the captured execução pair; the parent calls `process_event fechar_release` only after the child completed and `release-guard post` passes. Nothing goes to production without Alan's explicit request and cards homologated by him.

#### Scenario: Closeout with execution parent
- **WHEN** a batch is ready and Alan explicitly asks to close it in a Claude Code session observed on Sonnet 5.5 high
- **THEN** the agent steps follow the shared release rules and T16 is the only Status change made by the agent

#### Scenario: Wrong parent model refuses closeout
- **WHEN** the parent session is observed on a different model or effort, or unobserved
- **THEN** T16 and `fecho-lote` are refused visibly and production is untouched

### Requirement: Impeccable guidance fires under the same conditions
The Claude Code adapter SHALL run the shared Impeccable hook (`.agents/skills/impeccable/scripts/hook.mjs`, started by `claude_adapter.py` with `IMPECCABLE_HOOK_HARNESS=claude`) on `PostToolUse` file edits and on `Stop`, under the same conditions as the other clients, as advisory output that does not revert effects. `hook.mjs` and everything it imports (the whole `.agents/skills/impeccable/scripts/` tree) are part of the adapter digest the operator reviews.

#### Scenario: UI file edited in Claude Code
- **WHEN** a UI file covered by Impeccable is edited in a Claude Code session
- **THEN** the same detector guidance as in the other clients is added to the session context

### Requirement: Every Claude Code surface either works or fails visibly
Claude Code SHALL run locally, through the CLI on the operator's VM. This change SHALL prove the flow in the terminal (CLI) only; the surfaces that drive that local session (IDE and desktop over SSH to the VM, the web through Remote Control) are not claimed as proven by this change (Alan's decision, 2026-10-15; follow-up in #1103). Where any surface lacks the guard, the model selection or the required evidence, the stage MUST fail visibly on that surface, without fallback to another surface or client. The observed surface SHALL be recorded in evidence.

#### Scenario: Terminal is the proven surface
- **WHEN** a stage runs from a surface other than the terminal on the VM
- **THEN** the evidence records the observed surface and nothing in this change presents that surface as proven
- **AND** a missing guard, model selection or evidence on it fails visibly, without fallback

#### Scenario: IDE with an older embedded host
- **WHEN** the IDE's embedded Claude Code version lacks per-invocation effort or its transcripts do not match the evidence schema
- **THEN** the spawn or transition is refused visibly on that surface

### Requirement: Hooks protect only after operator trust review
Claude Code hooks SHALL be registered in the operator account through the `account-hook-shim` (user settings), not in the repository, and SHALL count as protection only after the operator explicitly reviews and records, on the host account, both digest parts: the registration part (the account hook block and the shim) and the adapter part (the adapter's Python modules, the Impeccable `hook.mjs` and the whole `.agents/skills/impeccable/scripts/**` tree it can load, and the other files listed for `claude` in the pinned adapter manifest). Pinning, installation or the host's workspace trust dialog MUST NOT stand in for this review. A session whose adapter digest is not recorded SHALL deny product writes and spawns and fail the evidence preflight. A registration digest that differs from the one recorded at session start SHALL require reopening the session (`hooks_changed`); an adapter digest that changed to another reviewed digest SHALL NOT require reopening. No bypass SHALL be used and no Auto mode SHALL be claimed.

#### Scenario: Changed adapter after review
- **WHEN** `claude_adapter.py`, a module it imports or any file under `.agents/skills/impeccable/scripts/**` changes after the recorded review
- **THEN** the session page reports unreviewed hooks, product writes and spawns are denied, and dependent transitions are refused

#### Scenario: Reviewed adapter change without reopening
- **WHEN** the adapter changes and the operator records the new adapter digest while the session stays open
- **THEN** the next hook call accepts the new digest without `/exit`, and the session heartbeat keeps its registration digest

#### Scenario: Registration change requires a new session
- **WHEN** the account hook block or the shim changes after the session started
- **THEN** dependent transitions and spawns are refused with `hooks_changed` until a new session starts

### Requirement: The adapter ships unofficial and integrates by the general T14 rule
This change SHALL deliver the Claude Code adapter as unofficial: neither `AGENTS.md`, the Project board description nor the canonical skill's active-client line SHALL name Claude Code as a client, and this change MUST NOT modify `AGENTS.md`, its renderer or pin, or the board description; officialization belongs to a separate follow-up card prioritized by Alan, opened after this card's Done técnico. No pilot card, client-switch card or `pilot_evidence` gate SHALL condition this card's Done técnico (cancelled by Alan on 2026-10-15): this change MUST NOT declare the `pilot_evidence` gate, and after QA green and a passing `review_process_checklist.py --phase postqa` the parent SHALL call `integrar_develop` in the same turn, as for any card. The `pilot_evidence` checklist item SHALL stay available only for a change that declares it. The T14 guard in `process_event` SHALL remain unchanged.

#### Scenario: T14 without a pilot gate
- **WHEN** this card is QA green and the postqa checklist passes
- **THEN** the parent calls `integrar_develop` for this card in the same turn
- **AND** the checklist does not evaluate `pilot_evidence`, because this change does not declare it

#### Scenario: Adapter stays unofficial
- **WHEN** this change is integrated
- **THEN** `AGENTS.md`, the board description and the active-client line do not name Claude Code as a client
- **AND** officialization is left to a follow-up card with Alan's T1

### Requirement: Installer reproduces the adapter and existing clients stay green
The nucleus pin installer SHALL reproduce the Claude Code adapter in the Cripto consumer (bridges and manifest, agents, scripts, policy contract and the `claude` entry of the adapter manifest) without writing a hook registration into the consumer, and SHALL refuse visibly on conflicts. The account installer SHALL register the Claude Code shim in the operator's user settings, preserving foreign hooks. Specs and tests SHALL cover the new client, and the existing Cursor, Codex, Grok, OpenCode and dsh tests SHALL keep passing, changed only where the Cursor, Codex or OpenCode hook registration moved to the account or the Codex collector accepts versions by schema; Grok and dsh tests SHALL not change.

#### Scenario: Pin installs the adapter
- **WHEN** the new pin is installed into a consumer fixture
- **THEN** the Claude Code files match the manifest, the resolver accepts `--client claude`, and no `.claude/settings.json` hook block of the Covenant Flow is written
- **AND** foreign hooks already in the consumer's `.claude/settings.json` are preserved

#### Scenario: Existing clients unchanged
- **WHEN** the process-fsm test suite runs after the change
- **THEN** all tests for the five existing clients pass, with only registration-location and version-acceptance expectations updated

### Requirement: Synthetic final turns fail only on API errors
A child whose last `assistant` turn is `<synthetic>` SHALL be classified `failed` only when that turn records an API error; a final `<synthetic>` turn without error SHALL be left out of the model comparison and the status SHALL come from the last real turn (R13).

#### Scenario: Final synthetic without error
- **WHEN** the child's last turn is `<synthetic>` without an error and the previous real turn completed with the captured pair
- **THEN** the child is `completed` with the observed pair of the last real turn

#### Scenario: Final synthetic with API error
- **WHEN** the child's last turn is `<synthetic>` recording an HTTP 429
- **THEN** the child is `failed` and the proxy records an unsuccessful attempt

### Requirement: Closeout parent check applies at the event
For the `claude` client, `process_event fechar_release` SHALL itself check that the parent session's observed model and effort match the captured `claude/execucao` pair before T16, refusing visibly when divergent or unavailable; the check SHALL NOT depend on the runbook being followed (R26). This applies the existing #1101 rule where the event happens and adds no gate.

#### Scenario: T16 from a judgment-model parent
- **WHEN** a Claude Code parent observed on Opus calls `process_event fechar_release`
- **THEN** the event is refused naming the observed and captured pairs, and Status is unchanged

### Requirement: First write of a real child is proven on a real transcript
The check before a child's first write (model and effort of the child's transcript against the capture) SHALL be proven in the live rehearsal with a real child transcript, not only with synthetic fixtures (R27).

#### Scenario: Real child first write
- **WHEN** a real execução child born in the rehearsal makes its first write
- **THEN** the receipt is marked verified when the pair matches, and a divergent pair is denied with `model_mismatch`

### Requirement: Batch closeout rehearsal only on Alan's request
The batch closeout rehearsal in Claude Code (#1101 task 9.6) SHALL run in this change only if Alan asks for it; otherwise his answer SHALL be recorded on the card and the task closed without the rehearsal (R35).

#### Scenario: Alan declines the closeout rehearsal
- **WHEN** Alan answers that he does not want the closeout rehearsal
- **THEN** the card records his answer and no closeout runs

### Requirement: Background child handback is recognized
Evidence collection (`claude_evidence.py collect`/`extract` and `claude_proxy.py`) SHALL recognize two forms of a child's return in the parent transcript: `<agent-message from="{agentId}">` and a `queue-operation` `enqueue` record carrying `<task-notification>`. A `<task-notification>` SHALL be accepted only when its `<task-id>` equals the child's `agentId` and its `<tool-use-id>` equals the spawn `call.id`. Its `<status>` SHALL map `completed` to `completed` with the `<result>` content as payload, `failed` to `failed` and `killed` to `interrupted`. A spawn returning `status="async_launched"` SHALL be accepted when its `resolvedModel` equals the captured model, or, when the spawn carries no `resolvedModel`, the model SHALL be checked on the return or on the child's turns. An unknown return form SHALL yield a visible `unsupported_schema` naming the field and SHALL NOT remain `terminal_unavailable` forever.

#### Scenario: Background child completed
- **WHEN** a child spawned with `async_launched` finishes and the parent transcript has a `<task-notification>` with matching `<task-id>` and `<tool-use-id>`, `<status>completed</status>` and a `<result>`, and the child's turns match the capture
- **THEN** the evidence is `completed` with the `<result>` content as payload and the proxy line shows the observed pair

#### Scenario: Background child failed
- **WHEN** the matching `<task-notification>` has `<status>failed</status>`
- **THEN** the evidence is `failed` and the proxy records an unsuccessful attempt

#### Scenario: Notification for another tool call
- **WHEN** a `<task-notification>` has the child's `<task-id>` but a `<tool-use-id>` different from the spawn `call.id`
- **THEN** it is not accepted as this child's return

#### Scenario: Unknown return form
- **WHEN** the parent transcript returns the child in a form that is neither `<agent-message>` nor a recognizable `<task-notification>`
- **THEN** collection fails with `unsupported_schema` naming the field, not `terminal_unavailable`

