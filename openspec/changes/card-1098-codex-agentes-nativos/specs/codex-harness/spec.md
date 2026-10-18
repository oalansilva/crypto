Scope revised on 2026-10-18: #1098 delivers the interactive CLI card-worktree route with native children and an automatic dedicated exec Review coordinator. Full refinement, all-stage/all-surface coverage, app/IDE and independent exec-principal routes remain pending in #1128 (former tasks 5.5/5.6/5.8 and multi-surface parts of 5.1/5.7/6.3). No transferred acceptance is completed. Safeguards below remain mandatory for every attempted stage; scope reduction does not establish universal support or waive CLI Review/QA.

## MODIFIED Requirements

### Requirement: Codex stage children are isolated and reviews use the exact diff
Refinement, Design authoring and critique, Apply, and QA SHALL use native Codex children linked to the card chat. Code Review SHALL use two native children of an automatically launched dedicated read-only Codex coordinator in the same card worktree. All children SHALL receive self-contained prompts without parent transcript, fork_turns=none, the operational context evidence criterion below and locally captured model/effort. The operator MUST locate each child and result through the linked native session identities. External sessions for other delegated stages, hidden fallback and review execution by principal or coordinator MUST NOT be used. Review children MUST receive the same principal-materialized exact diff and digest, remain effectively read-only and return independent findings. Missing, interrupted, blocked or unverified attempts MUST NOT count as successful stages. This dedicated coordinator exception supersedes same-card-chat requirements below only for Review; it does not qualify other surfaces or stages.

#### Scenario: Design and QA are separate children
- **WHEN** the parent enters Design or QA and the host capability preflight passes
- **THEN** it spawns a native stage child in the same card chat with only the stage context and the captured pair
- **AND** the parent does not execute that stage's authoring or checks in its own transcript
- **AND** the operator can inspect the child's state, steer it using available native controls, and locate its returned payload

#### Scenario: All delegated stages preserve native visibility
- **WHEN** refinement, Design critique, Apply, or either review role is delegated
- **THEN** the child is linked to the card chat with a stable identity and role, or, for Review only, to its dedicated coordinator through the verified principal/coordinator/child chain
- **AND** birth, execution, result and interruption evidence refer to that same identity
- **AND** no external orchestration session is presented as a native child

#### Scenario: Two read-only reviewers inspect one interval
- **WHEN** Code Review begins with a materialized pre-commit or closing diff and an automatically launched dedicated coordinator verified read-only from birth
- **THEN** diff-reviewer and code-reviewer are spawned in the same coordinator turn as distinct native children with separate prompts and the same exact path and SHA-256
- **AND** neither fetches another diff from git, supplies the parent transcript, or bypasses the documented-contract/native-call/complementary-essay criterion
- **AND** runtime evidence proves the coordinator and both children stay read-only until both complete with payload, while the principal remains writable
- **AND** a controlled isolation essay proves each reviewer can read the diff and that each reviewer's write attempt is denied with unchanged target bytes
- **AND** their findings and completed status are recorded separately before the writable parent persists proxies

#### Scenario: Incomplete child blocks stage success
- **WHEN** a child is interrupted, lacks a result, runs under the wrong model or effort, or lacks required runtime evidence
- **THEN** that stage does not advance as a successful child execution
- **AND** the parent reports the actual failure or unavailable evidence without synthesizing completion

#### Scenario: Review host cannot prove effective read-only permissions
- **WHEN** the route lacks a supported and verifiable dedicated coordinator born read-only and governing native review children
- **THEN** the parent refuses the review before review work or reviewer spawns
- **AND** it names the missing guarantee without asking the operator to alternate permissions or relaxing review gates
- **AND** a role file or instruction claiming read-only does not satisfy the gate

## ADDED Requirements

### Requirement: Codex automatically coordinates Review with a verified session chain
The writable principal SHALL prepare an exact diff package, SHA-256, captures, prompts, probe plans and pending birth envelopes, automatically launch a dedicated Codex coordinator read-only in the same card worktree, and persist evidence after both native reviewers complete with payload. Runtime sources MUST prove principal launch → real coordinator → two distinct role children, same coordinator turn, card/worktree/diff, stable selection and effective read-only permissions. Pending envelopes MUST be an explicit schema state and MUST NOT claim final parent binding or completion. Binding SHALL be resolved only from authoritative launch and spawn sources; arbitrary parent ids, rewritten traces and retroactive fabricated receipts MUST be rejected. Each reviewer SHALL verify the package and complete its fixed-helper diff-read/write-denial/readback probe before review work. verify-wave and the process checklist MUST pass before commit. No daily operator permission toggle, automatic trust or review in principal/coordinator SHALL be permitted.

#### Scenario: Automatic dedicated wave completes
- **WHEN** the qualified launcher starts a coordinator with a supported read-only sandbox and verified card/worktree/selection/context
- **THEN** two native role children are born in its same turn and remain read-only with the coordinator through both completed payloads
- **AND** the writable principal collects source-verified receipts and findings using the actual coordinator binding before verify-wave and checklist
- **AND** no manual permission switch is required

#### Scenario: Named role permits only its diagnostic probe attempt
- **WHEN** a reviewer receives its verified fixed-helper plan and precreated disposable fixture
- **THEN** its explicit role contract permits only that controlled attempt and requires denied writing with unchanged bytes before review
- **AND** successful writing, an arbitrary target, missing native probe events or conflicting role restrictions fail the wave
- **AND** final verify-wave is not required before generating the evidence it consumes

#### Scenario: Dedicated source or binding is unavailable
- **WHEN** the launcher cannot prove the real coordinator identity or the preflight cannot validate the source-backed chain before reviewer work
- **THEN** the attempt is refused without treating a principal-bound receipt as coordinator-bound or changing source evidence
- **AND** a TUI default diagnostic positive does not qualify exec dedicated, named reviewer profiles, app/IDE transport or product review

#### Scenario: Interactive CLI launches its exec coordinator
- **WHEN** interactive CLI launches the dedicated exec coordinator
- **THEN** qualification separately covers the CLI launch/return route and the coordinator surface with actual native evidence for the final code
- **AND** missing route capabilities remain blockers; historical diagnostics or documented commands do not qualify the final product wave
- **AND** independent exec/app/IDE principal routes remain pending under #1128 without a support claim

#### Scenario: Large diff and asynchronous execution preserve complete evidence
- **WHEN** the diff requires multiple pages or preflight/probe execution returns asynchronously
- **THEN** each reviewer MUST read the complete same artifact, with byte coverage and digest reconstruction in native CommandExecution and the result delivered to the model
- **AND** missing, duplicate, out-of-order or truncated pages fail; summaries and manifests do not replace the diff
- **AND** the fixed probe runs once and asynchronous execution awaits that same process/cell to completion without rerunning the write attempt
- **AND** insufficient real capacity blocks findings without reducing the reviewed interval

### Requirement: Codex qualifies capabilities independently for each operator surface
The harness SHALL qualify the delivered interactive CLI → dedicated exec coordinator route using verifiable schema, origin and session capabilities, not an exclusive host-name comparison with codex_exec. Host/version SHALL remain diagnostic provenance. Qualification MUST be backed by real native success and refusal on the observed route with revalidated source integrity and final-code scope. Fixtures and qualification copied from another surface MUST NOT establish support. Legacy exec evidence MUST remain readable without permitting surface relabeling. Every required lifecycle, worktree, selection and permission check MUST remain enforced. Full interactive refinement, independent exec-principal and app/IDE qualification are transferred to #1128; investigating schemas or documenting limitations MUST NOT count as completed positive acceptance.

#### Scenario: Interactive CLI delegation succeeds natively
- **WHEN** a qualified interactive session meets all guarantees for an authorized stage of the delivered CLI workflow
- **THEN** it can complete that stage with a native isolated child and verified evidence in the same chat, using the dedicated verified chain only for Review
- **AND** it is not redirected to exec because its originator is codex-tui

#### Scenario: Dedicated exec retains its verified role
- **WHEN** the CLI-launched exec coordinator supplies compatible schema and all required native evidence after adaptation
- **THEN** preflight and collection succeed for that dedicated role without granting independent exec-principal qualification
- **AND** legacy exec proof cannot be relabeled to qualify TUI or app

#### Scenario: App or IDE lacks a guarantee
- **WHEN** an app/IDE session lacks a required verifiable field, native linkage, qualification or isolation capability
- **THEN** the affected stage is refused with the specific missing guarantee and surface identified
- **AND** state and human gates are preserved; no universal support or executed stage is claimed
- **AND** missing acceptance remains in #1128; documented limitation does not complete a positive essay

#### Scenario: Name and version do not replace validation
- **WHEN** a session exposes a compatible schema but a different diagnostic host name or version
- **THEN** the driver validates origin, surface qualification and all required guarantees
- **AND** missing fields or incompatible schema still fail explicitly and a different surface cannot reuse exec qualification

### Requirement: Codex preflights native delegation guarantees before stage work
The orchestrator MUST check native chat linkage, the selected operational context criterion, applied model/effort observability, authorized working context, and effective permissions for the requested stage before its work begins. The context preflight MUST require an applicable documented contract, an intact surface-specific complementary essay qualification, and prepared fork_turns=none arguments; the actual native call MUST be revalidated for each birth. Internal full-context attestation SHALL remain unavailable and SHALL NOT be required by this context criterion. Other known unavailable required capabilities MUST produce a visible refusal before spawn. Where another required runtime verification requires a child to exist, the host MUST support withholding stage work until the verification passes; otherwise the spawn MUST be refused. Refusal MUST identify card, stage, missing guarantee and non-executed outcome without changing FSM state or human gates.

#### Scenario: Capability is known missing
- **WHEN** the host lacks required directory/linkage/model-observation evidence or any required part of the selected operational context criterion
- **THEN** the parent reports which stage cannot begin and why
- **AND** it does not spawn for stage execution, substitute a model, change trust, or launch an external session

#### Scenario: Startup verification fails
- **WHEN** a native diagnostic-only child is supported and its startup metadata is absent or differs from the captured selection or authorized context
- **THEN** no stage work is released to that child
- **AND** the failure records the actual child identity and unavailable or divergent values
- **AND** the diagnostic birth is not counted as completed stage execution

### Requirement: Codex validates the effective card worktree independently of tool paths
The adapter MUST distinguish session/card authorization, tool working directory, and mutation targets. It SHALL normalize only observed supported host payload schemas, verify the canonical card worktree and branch against the bound card and current FSM authorization, validate all effective paths, and use that verified context with the existing Guard. A supplied workdir or prompt MUST NOT authorize another checkout or stage. Missing identity, unresolved ambiguity, escaped paths, or unsupported hook coverage MUST yield a visible refusal of the affected work. Refinement SHALL retain the existing issue-bound pre-worktree context; post-T1 children SHALL operate in the bound card worktree.

#### Scenario: Authorized Design write after native same-chat resumption
- **WHEN** the session originally starts in source but the operator resumes the same chat natively in the card worktree and active turn_context, child birth metadata and all child turns prove that effective binding
- **THEN** the Guard permits the authorized OpenSpec artifact write there
- **AND** command result, target readback and Guard context prove the same card and worktree
- **AND** historical session_meta cwd does not override the verified current turn
- **AND** a shell workdir or root argument alone cannot establish this binding or authorize another card

#### Scenario: Native resumption does not prove child completion
- **WHEN** preflight becomes ready after same-chat resumption and a birth receipt is prepared
- **THEN** completion still requires source-verified child lifecycle and returned payload
- **AND** neither the receipt nor a Design artifact write proves Guard enforcement or effective read-only isolation

#### Scenario: Workdir cannot impersonate another card
- **WHEN** a call supplies another card worktree, escaped symlink target or mixed unauthorized mutation paths
- **THEN** the covered write is denied before mutation and readback proves targets unchanged
- **AND** no supplied path changes the authorized card identity

#### Scenario: Stage gate remains active
- **WHEN** a bound Design or Todo card attempts a product write through a covered command or edit route
- **THEN** the existing Guard denies it before mutation
- **AND** a legal product fixture write after T8 is allowed only in the authorized card worktree

#### Scenario: Hook resolves the wrong checkout or does not run
- **WHEN** the native command uses the intended worktree but its hook uses another checkout or cannot provide the required interception evidence
- **THEN** the operation is not claimed as proven safe or as a successful solution to the directory failure
- **AND** affected work is refused without launching a replacement session or bypassing hook trust

### Requirement: Codex records requested and observed native lifecycle evidence separately
Each attempt MUST retain the birth selection capture, actual native arguments, card/stage/role/chat/child identity, effective worktree, runtime host/version, effective permissions, lifecycle events and returned payload evidence with provenance. Requested model and effort MUST remain distinct from runtime-observed values and MUST match the validated birth capture. Operational context evidence MUST separately retain the applicable documented runtime contract, the actual source-registered native fork_turns=none call and the complete complementary non-secret essay described below. It MUST NOT claim to attest the complete internal context. Missing values SHALL remain unavailable and fail gates that require them; full internal-context attestation is explicitly unavailable and is not a prerequisite of the selected operational context criterion; completed SHALL require a returned payload associated with the same child. Review wave validation SHALL retain two distinct roles and children, stable captured selection, exact diff SHA-256, effective read-only proof, and both successful payloads.

#### Scenario: Requested pair is not observed telemetry
- **WHEN** a native spawn accepts the captured model and effort but returns only a task identity and result
- **THEN** the evidence records the requested pair and marks missing observed values unavailable
- **AND** it does not report selection verified or mark the proxy successful

#### Scenario: Valid completed native delegation
- **WHEN** source-verified evidence validates the captured pair, actual native call, documented-contract/complementary-essay context criterion, correct worktree and effective permissions and the child completes with payload
- **THEN** the record relates birth, execution, completion and content to the same card, stage and child
- **AND** the operator can find the child and its result in the card chat

#### Scenario: Partial or interrupted review wave
- **WHEN** either reviewer is interrupted, fails, lacks payload or lacks runtime/digest evidence
- **THEN** the wave remains unsuccessful even if the other reviewer completed
- **AND** no review approval, commit gate or QA transition is justified by that wave

#### Scenario: Separate waves each return one reviewer
- **WHEN** one role completes in one wave and the other completes in another wave or coordinator turn
- **THEN** the results MUST NOT be combined into an accepted pair even if their diff digest matches
- **AND** verify-wave and checklist remain blocked until a complete same-turn wave satisfies all guarantees

### Requirement: Codex reports proven host coverage without declaring partial replacement complete
Acceptance evidence MUST distinguish unit/contract tests, runtime facts, operator-interface observations, and unavailable guarantees for the delivered interactive CLI workflow and dedicated exec Review coordinator. The native path SHALL be demonstrated on the real host for successful delegation and a refused attempt, authorized and unauthorized writes, the scoped operational context evidence and selection observations, lifecycle visibility and the complete read-only review wave. CLI QA MUST remain mandatory after valid Review/checklist through the canonical flow. Unproved required CLI acceptances MUST remain pending and MUST NOT count as completed delivery. Transferred all-stage/all-surface acceptances MUST remain pending in #1128; scoped CLI completion MUST NOT claim integral replacement across those surfaces. Documentation SHALL describe proven coverage and refusal behavior without claiming Auto or changing other clients.

#### Scenario: Host exposes only part of the required capability
- **WHEN** native authoring can return content but runtime selection or read-only review remains unproved
- **THEN** the evidence identifies precisely the observed capabilities and blocked stages
- **AND** refusal tests may pass while positive runtime acceptance remains pending
- **AND** the CLI card is not reported complete while its required acceptances remain pending, nor as an integral all-surface substitution after scoped completion

#### Scenario: Operator verifies live visibility and interaction
- **WHEN** a supported stage is exercised on the real operator surface
- **THEN** evidence shows the responsible child in the native list, its running state, inspection or steering through supported controls, and its returned content in the chat
- **AND** failure and interruption are displayed as such rather than completed results

### Requirement: Codex evaluates operational context using a documented contract and a controlled complementary essay
The selected context criterion SHALL require all of: a documented contract applicable to the observed runtime surface and native tool, a source-registered native birth call with fork_turns=none and parent/chat/turn/child provenance, and a complete complementary non-secret essay of unintended history inheritance qualified for that surface and contract. Documentation from another product, configuration, a prepared receipt, child prose or a sentinel's absence alone MUST NOT satisfy the criterion. Full internal-context attestation SHALL remain explicitly unavailable; a positive operational result MUST NOT be described as an attestation of the complete context delivered internally to the model. This scoped criterion MUST NOT replace or relax model/effort observations, Guard, effective read-only permissions, reviewer diff read/write-denial/readback evidence, lifecycle gates or human approval.

#### Scenario: Complete controlled essay satisfies the scoped operational criterion
- **WHEN** the parent establishes a new non-secret sentinel S only in its earlier context and delivers a distinct positive-control marker C in the child's self-contained diagnostic prompt
- **AND** S is not supplied through that prompt, steering, shared files, fixtures, environment variables, names or other child-visible channels, and the child does not retrieve parent transcripts or contamination sources
- **AND** the applicable documented contract and the actual native fork_turns=none call, identities and source digests are validated
- **AND** the same child completes with payload returning C exactly and reports no inherited S
- **THEN** the essay may qualify the observed operational context criterion for that surface and contract
- **AND** its result explicitly states that S's absence alone is insufficient and complete internal-context attestation remains unavailable

#### Scenario: Parent sentinel or native call diverges
- **WHEN** an uncontaminated essay returns the parent-only sentinel without authorized delivery, or the source-registered birth call differs from fork_turns=none
- **THEN** the result is divergent, qualification and dependent work are blocked, and no positive context evidence is recorded
- **AND** changing models or repeating the attempt does not erase the recorded divergence

#### Scenario: Missing control or contaminated essay is not positive
- **WHEN** C is absent or incorrect, the child is interrupted, payload or provenance is incomplete, or S reached a child-visible channel
- **THEN** the essay is incomplete or invalid and does not qualify the surface or release dependent stage work
- **AND** silence or an absent S does not convert that result to success

#### Scenario: New diagnostic invalidates reuse of older success
- **WHEN** a newer applicable diagnostic birth is failed, incomplete, divergent or lacks qualification artifacts
- **THEN** an older successful qualification MUST NOT authorize dependent work
- **AND** native source order and integrity, rather than a selected success path or file timestamp, determine the applicable attempt

#### Scenario: Documentation or surface qualification cannot be substituted
- **WHEN** only generic multi-agent documentation, another surface's essay, configuration or a declared isolation value is available
- **THEN** the required documented-contract/native-call/complementary-essay set remains unverified
- **AND** app-server excludeTurns response pagination is not treated as native fork_turns=none or proof of non-inheritance

#### Scenario: Internal attestation remains unavailable after a positive essay
- **WHEN** all three operational evidence parts pass but the provider does not expose complete internal context telemetry
- **THEN** the record separates contractual evidence, empirical observations and internal_context_attestation=unavailable with their provenance and scope
- **AND** this unavailable attestation alone does not fail the revised context criterion or supply any other missing required guarantee
