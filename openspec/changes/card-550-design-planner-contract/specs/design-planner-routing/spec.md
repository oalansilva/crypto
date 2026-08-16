## ADDED Requirements

### Requirement: Exact OpenCode runtime compatibility

The Design-gate adapter SHALL initially support exactly OpenCode `1.18.18`. It SHALL use only fields observed in that version: session ID, parent, version and time from `session.created`; session, agent, provider/model, variant, and optional input `messageID` from `chat.message`; tool, session, call and args from `tool.execute.before/after`; and session, message, agent, directory and worktree from custom-tool context. It MAY use the observed SDK contracts: `client.session.create` with `body.parentID`, `body.title`, and `query.directory`, returning a Session ID; and `client.session.prompt`/`promptAsync` with session path ID and body `agent`, `model`, optional `messageID`, `parts`, and optional `tools`. Variant SHALL come from the selected agent profile and SHALL be verified in `chat.message`. An adapter test SHALL prove the runtime `AssistantMessage`/parts schema and whether `ToolContext.messageID` identifies that assistant message before the writer is enabled. The adapter SHALL NOT require a task invocation ID, pre-spawn child ID, suspended-child API, or an unverified TypeScript filesystem API.

#### Scenario: Installed runtime is exactly compatible

- **WHEN** the host reports `1.18.18` and adapter tests recognize every required event and runtime DB schema
- **THEN** a run may proceed subject to all remaining checks

#### Scenario: Runtime version or schema is unknown

- **WHEN** the version differs, a required field/schema is absent, or correlation is ambiguous
- **THEN** the run is `BLOCKED`
- **AND** compatibility SHALL NOT be inferred from a similar version

### Requirement: Trust boundary is process-scoped and explicit

For #550, the TCB SHALL contain only: the OpenCode `1.18.18` process, the loaded dedicated guard module instance, each exact native writer-helper process launched by that guard, and each exact read-only OpenSpec-runner process launched by that guard. Evidence for each component/invocation SHALL record PID, PPID, absolute executable, actual executable/build digest, `build_id`, `module_instance_id`, protocol version, and exit/result; each run SHALL also record the external `deployment_manifest_sha256` used by the verifier. Main, models, and tools SHALL be observed subjects, not implicit trusted components. Every other process SHALL remain outside the TCB.

Owner-only storage, a hash chain, and sidecar digests SHALL be described and tested as accidental-failure detection and correlation mechanisms, not as tamper-proof protection against the same OS user. The #555 attestor SHALL remain the future external trust mechanism.

#### Scenario: Evidence is evaluated inside the declared boundary

- **WHEN** plugin events, runtime DB records, journal bytes, and artifact digests correlate
- **THEN** the process-trusted verifier may accept that correlation
- **BUT** it SHALL NOT claim resistance to fabrication by the same OS user
- **AND** same-user or administrator tampering SHALL remain outside the #550 threat model

#### Scenario: Another process or OS user edits storage

- **WHEN** an external process or user modifies an artifact or evidence source
- **THEN** #550 makes no prevention or tamper-proof claim for that actor
- **AND** a persistent artifact difference SHALL still be rejected if it lacks an authorized call chain

#### Scenario: A transient external edit is restored

- **WHEN** an out-of-process edit is restored before any governed observation or final inventory
- **THEN** the implementation SHALL NOT claim that #550 detects it

### Requirement: Dedicated project-local guard and enumerated tools

The implementation SHALL add a project-local `design-gate-guard.ts`, `design_artifact_write`, `design_spawn_stage`, and `design_openspec_readonly`, plus the dedicated native writer helper and read-only OpenSpec runner/adapter. It SHALL NOT modify an existing general-purpose plugin to implement this contract. During a lease, the guard SHALL broadly deny every native tool, custom tool, and MCP capability that is not explicitly enumerated for the bound role.

#### Scenario: Dedicated guard is loaded

- **WHEN** a Design run starts
- **THEN** evidence identifies the dedicated loaded guard build
- **AND** only the three contract tools are registered for their respective roles

#### Scenario: Unknown tool or general plugin is used

- **WHEN** a session requests an unknown native/custom/MCP tool or implementation changes a general plugin for this contract
- **THEN** the request or scope check fails
- **AND** the run remains `BLOCKED`

### Requirement: Candidate author has only the guarded writer

The system SHALL first validate `design-planner-candidate-v1` with `mode: subagent`, `model: openai/gpt-5.6-sol`, and configured `variant: high`. Its ordered permission rules SHALL place broad deny before the final allow for `design_artifact_write`. It SHALL have no read, glob, grep, bash, task, network/web, native edit/write/apply_patch, skill, unknown custom/MCP, or other tool. All source, template, and instruction bytes SHALL be embedded in its packet, so the author SHALL NOT require a read tool.

#### Scenario: Candidate author receives its effective capability

- **WHEN** the candidate author is spawned with a valid packet
- **THEN** effective policy exposes only `design_artifact_write`
- **AND** runtime evidence observes `openai/gpt-5.6-sol` and variant `high`

#### Scenario: Candidate author requests another capability

- **WHEN** it requests any non-writer tool or an unlisted path
- **THEN** the request is mechanically denied
- **AND** the run is `BLOCKED`

### Requirement: Candidate critics have zero tools

The system SHALL validate `design-critic-readonly-candidate-v1` with `mode: subagent`, `model: openai/gpt-5.6-sol`, configured `variant: high`, and effective deny for every tool. A critic SHALL receive exact input bytes in its prompt and return response text only.

#### Scenario: Zero-tool critic returns usable structured output

- **WHEN** a critic returns non-empty schema-valid bytes without a tool call
- **THEN** its exact output parts and hashes are recorded
- **AND** runtime evidence SHALL observe Sol and variant `high`

#### Scenario: Critic attempts any tool

- **WHEN** a critic attempts a native, custom, or MCP tool
- **THEN** the attempt is denied and recorded
- **AND** that Assessment is `BLOCKED`

### Requirement: Independent pre-build ID and post-build deployment manifest prove loaded bytes

Every candidate and canonical validation SHALL run in a newly started OpenCode process. Before compilation, the build pipeline SHALL choose a `build_id` independent of final output hashes, either a UUID or canonical `commit+nonce`, and SHALL embed only that `build_id` plus protocol version in the guard, native writer helper, and read-only runner. The `build_id` SHALL NOT be derived from content that embeds it or from any final-file hash.

After all builds finish, the pipeline SHALL generate canonical `deployment-manifest.json` bytes containing `build_id`, OpenCode version/digest, OpenSpec executable version/digest, and the actual final hashes of the agent files, guard build, native writer helper, read-only runner/adapter, and schema/config. It SHALL then calculate `deployment_manifest_sha256` from those final manifest bytes. `deployment_manifest_sha256` SHALL NOT be embedded in any binary or module. Every loaded/runtime component SHALL report `build_id` and a fresh `module_instance_id`; the verifier SHALL hash the actual executable/build/file bytes and require equality with the external deployment manifest and its `build_id`.

Evidence SHALL record PID, PPID, absolute executable, actual executable/build digest, `build_id`, `module_instance_id`, `deployment_manifest_sha256`, protocol version, `process_started_at`, child session times, and terminal exit/result where applicable for every enumerated TCB component/invocation.

#### Scenario: Fresh loaded build is observed

- **WHEN** sessions are created after process start, every TCB identity/result field is present, reported build/protocol/module identity agrees, `deployment_manifest_sha256` verifies the external manifest bytes, and actual bytes match that manifest
- **THEN** process-freshness validation may pass

#### Scenario: Session, process, or loaded build is stale

- **WHEN** a session predates process start, a previous process is reused, a TCB field is absent, actual bytes differ from `deployment-manifest.json`, `build_id`/protocol/module identity mismatches, `deployment_manifest_sha256` is wrong or embedded, a self-referential ID is used, or only an unbound current disk hash is available
- **THEN** validation is `BLOCKED`

### Requirement: Main-only spawn tool creates the sole lease-bound child

`design_spawn_stage` SHALL be a main-only custom tool and the only spawn operation permitted by a lease. It SHALL validate a `CREATED` lease, its parent session, canonical directory, and sealed manifest; preallocate a cryptographically unique UUID `input_message_id`; call `client.session.create` with exact `parentID`, title, and directory; record the returned child Session ID; and call `client.session.prompt` or `promptAsync` for that ID with `body.messageID` exactly equal to `input_message_id` plus the exact sealed agent, model, and parts. It SHALL supply no tool override that broadens the selected profile. Variant SHALL come from the candidate profile and SHALL be verified in the first `chat.message`.

The author and critic profiles SHALL retain `task: deny`, and main SHALL NOT use Task during the lease. A custom plugin tool MAY call this SDK without shell. Any alternate spawn path, create/prompt failure, empty result, child mismatch, or profile-expanding tool override SHALL finalize `ABORTED/BLOCKED`.

#### Scenario: Bound SDK spawn succeeds

- **WHEN** `design_spawn_stage` validates a `CREATED` lease and SDK create/prompt return one matching child with the preallocated input message ID, sealed agent, model, parts, parent, and directory
- **THEN** the child ID is durably recorded
- **AND** no other spawn mechanism is accepted for that lease

#### Scenario: Spawn bypass or mismatch occurs

- **WHEN** main uses Task, another tool/API spawns the child, an SDK call fails, output is empty, IDs differ, or a tool override broadens the profile
- **THEN** the lease finalizes `ABORTED/BLOCKED`

### Requirement: Preallocated input and runtime assistant messages bind without ID conflation

Before spawning a child, the guard SHALL create canonical manifest bytes with `run_id`, a cryptographically unique single-use manifest nonce, stage, sources/digests, exact paths, expected artifacts, expected agent/model/variant, parent, canonical worktree, packet/config/version digests, `build_id`, `deployment_manifest_sha256`, and process identity. The manifest SHALL not require a child ID. `design_spawn_stage` SHALL preallocate a UUID `input_message_id` before prompting and pass it as `client.session.prompt`/`promptAsync body.messageID` together with agent, model, and parts.

On `session.created`, the guard SHALL record child and parent. The child input `chat.message` SHALL create a provisional binding only when its optional `messageID` is present and exactly equals the preallocated `input_message_id`; session, agent, provider/model, variant, marker, and complete packet bytes SHALL also match. Absence or mismatch SHALL block provisional binding.

For an author, `ToolContext.messageID` SHALL be treated as `assistant_message_id` only after the OpenCode `1.18.18` adapter test proves that semantic. Before any filesystem action, the plugin SHALL query the corresponding runtime `AssistantMessage` and require child `sessionID`, `parentID == input_message_id`, and unique correlation to the hook-observed `callID` and single-use `operation_nonce`. It SHALL verify the sealed marker and packet in the input-message parts, not confuse those parts with the assistant/tool message, and then finalize binding. If the installed version does not provide this tested semantic, the run SHALL block before filesystem access.

For a zero-tool critic, after completion the adapter SHALL resolve exactly one output `AssistantMessage`, its parts, hashes, and result with child `sessionID` and `parentID == input_message_id`. Absence, ambiguity, or a different parent SHALL block. The nonce SHALL be consumed only on final binding. `input_message_id` and `assistant_message_id` SHALL remain distinct fields.

#### Scenario: Input message creates provisional binding and author finalizes with its assistant child

- **WHEN** parent, marker, packet, process, agent, model, variant, session, worktree, version, and `chat.message.messageID == input_message_id` agree provisionally, and the first writer context identifies a tested runtime `AssistantMessage` whose session is the child, parent is that input, and call/operation mapping is unique
- **THEN** the manifest nonce is consumed exactly once
- **AND** the lease may transition from `CREATED` to `BOUND`

#### Scenario: Zero-tool critic finalizes after completion

- **WHEN** provisional identity agrees and runtime DB resolves exactly one output `AssistantMessage` and its parts/hashes/result with `parentID == input_message_id` after completion
- **THEN** the critic binding may finalize without a tool call

#### Scenario: Binding data is absent, stale, reused, or ambiguous

- **WHEN** any required value is missing, mismatched, reused, or non-unique
- **THEN** no writer call is accepted
- **AND** the run transitions toward `ABORTED/BLOCKED`

#### Scenario: Filesystem action arrives before final binding

- **WHEN** a writer attempts any filesystem action before its context message finalizes binding
- **THEN** the guard denies and records it
- **AND** the run is `BLOCKED`

#### Scenario: Runtime message semantics are unavailable

- **WHEN** the adapter cannot prove that `ToolContext.messageID` identifies the required `AssistantMessage`, cannot query its child session/parent, or cannot correlate its call and operation nonce
- **THEN** no filesystem action is attempted
- **AND** the run is `BLOCKED`

### Requirement: Manifest and packet are byte-immutable

The manifest SHALL be canonical JSON addressed by SHA-256. Sources SHALL contain exact bytes or embedded content-addressed snapshots, not unresolved filesystem references. The prompt SHALL contain both the structured marker and the complete canonical packet bytes in a deterministic base64 envelope or deterministic text parts, with `packet_sha256`, encoding, and byte length. The plugin SHALL hash the actual input-message parts observed by `chat.message`, reconstruct the packet bytes, and bind those bytes and their digest to the manifest. A marker or filesystem reference without packet bytes SHALL be invalid. Packet, manifest, process, config, profile, schema, helper/runner, loaded guard, `build_id`, and external `deployment_manifest_sha256` SHALL agree. Text instructions SHALL NOT broaden permissions or paths.

#### Scenario: Sealed bytes agree

- **WHEN** actual message parts reproduce the complete canonical packet and every embedded source and contract component agrees with its sealed digest
- **THEN** immutable-input validation passes

#### Scenario: Any sealed component changes

- **WHEN** packet bytes are absent, actual input parts differ, or a packet, source, policy, profile, schema, helper/runner, build, deployment manifest, plugin, process, or version digest differs
- **THEN** binding fails closed
- **AND** a new run and nonce are required

### Requirement: Writer correlates callID with a single-use operation nonce

`design_artifact_write` SHALL require a single-use `operation_nonce`, manifest nonce/digest, exact path, base digest, and exactly one data-only full-content or safe-patch operation. The model SHALL NOT supply a trusted `callID`.

Path authorization SHALL require byte-for-byte equality with one manifest `exact_write_paths` entry, never a glob or prefix. Full content SHALL carry explicitly encoded complete bytes. A safe patch SHALL contain ordered, non-overlapping byte ranges with expected old-byte digests and replacement bytes; it SHALL execute no command or script.

At `tool.execute.before`, the guard SHALL validate the provisional input binding and atomically create one mapping `(sessionID, operation_nonce, argsHash) -> callID`. No more than one writer call SHALL be in flight per session/manifest. At custom-tool entry, context SHALL validate sessionID, agent, directory, and worktree. Only after the adapter test proves the semantic, it SHALL name `ToolContext.messageID` as `assistant_message_id`, query that runtime `AssistantMessage`, require its session to equal the child and `parentID == input_message_id`, correlate it uniquely with the mapped `callID`/`operation_nonce`, verify marker/packet in the separate input-message parts, finalize binding, and then atomically consume that unique mapping before any filesystem action.

#### Scenario: Bound single-flight call is correlated

- **WHEN** exactly one before-hook mapping matches the custom-tool context and exact args hash
- **THEN** the mapping and operation nonce are consumed before writing
- **AND** the recorded transition uses the hook-observed callID

#### Scenario: Nonce, mapping, context, or concurrency is invalid

- **WHEN** an operation nonce is reused, calls overlap, mappings are absent/multiple, args differ, or context mismatches
- **THEN** no write is accepted
- **AND** the run is `BLOCKED`

#### Scenario: A consumed operation fails

- **WHEN** the helper fails after mapping consumption
- **THEN** that operation nonce SHALL remain consumed
- **AND** recovery SHALL abort rather than retry it under the same nonce

#### Scenario: Path or data operation is not exact

- **WHEN** a path is a sibling/prefix/traversal variant or a request contains both/neither operations, overlapping ranges, stale replaced-byte digest, script, or command
- **THEN** the writer denies it before helper invocation
- **AND** the run is `BLOCKED`

### Requirement: Safe writer uses a dedicated Linux helper

The plugin SHALL invoke the dedicated Linux executable approved by external `deployment-manifest.json` by absolute path, with `shell: false`, fixed argv, minimal environment, and a canonical stdin protocol. The helper SHALL accept no command strings or alternate executables. It SHALL perform an explicit kernel/syscall/helper feature probe before enabling writes and SHALL report PID, PPID, absolute executable, actual digest, `build_id`, `module_instance_id`, protocol version, and exit/result for every invocation.

The helper SHALL anchor paths by dirfd and `openat2` with `RESOLVE_BENEATH|RESOLVE_NO_SYMLINKS`, validate regular-file ownership/link count/base digest, create a same-parent temp with `O_CREAT|O_EXCL|O_NOFOLLOW`, write/fstat/fsync, revalidate, install with `renameat2` or a tested `renameat` path, and fsync the directory. The implementation SHALL NOT depend on TypeScript exposing `openat2`.

#### Scenario: Full content is safely installed

- **WHEN** feature probe, dirfd/openat2 resolution, inode/base checks, write, fsync, rename, and directory fsync all pass
- **THEN** the helper returns structured before/after digests
- **AND** the guard records the authorized transition

#### Scenario: Safe patch is installed

- **WHEN** every byte range is ordered, non-overlapping, in bounds, and matches its old-byte digest
- **THEN** complete new bytes are derived before invoking the same safe installation path

#### Scenario: Host or filesystem capability is unsafe

- **WHEN** kernel/syscall/helper/build probe mismatches, required resolve flags are unavailable, traversal/symlink is found, an inode/base is unsafe, or rename/fsync fails
- **THEN** no destination state is accepted
- **AND** the run is `BLOCKED` without a TypeScript fallback

### Requirement: Lease follows a durable fail-closed state machine

Every run SHALL persist a lease with `run_id`, owner OpenCode PID/module instance, deadline, manifest nonce, and state. Allowed transitions SHALL be `CREATED -> BOUND -> FINALIZING -> CLOSED`, `FINALIZING -> ABORTED`, and early `CREATED|BOUND -> ABORTED`. In `CREATED`, `design_spawn_stage` MAY create exactly one child and the input `chat.message` MAY add provisional identity only with `messageID == input_message_id`; `BOUND` requires final author `AssistantMessage` binding at first writer entry or final critic output `AssistantMessage`/parts binding after completion, always with `parentID == input_message_id`. New operations SHALL be denied in `FINALIZING`, `CLOSED`, and `ABORTED`.

Journal/evidence finalization and fsync SHALL occur before lease release. Manifest and operation nonces SHALL be tombstoned and never reused.

#### Scenario: Successful run closes normally

- **WHEN** baseline, binding, calls, evidence, DB/events, and final artifacts all reconcile
- **THEN** the lease transitions through `FINALIZING` to `CLOSED`
- **AND** it is released only after the terminal journal is durable

#### Scenario: Empty, denial, crash, deadline, or evidence failure occurs

- **WHEN** a spawn is empty, a call is denied, a crash/deadline is detected, or evidence cannot reconcile
- **THEN** the run finalizes as `ABORTED/BLOCKED`
- **AND** lease release occurs only after durable terminal evidence

#### Scenario: Startup finds an orphan lease

- **WHEN** owner PID/module is stale, deadline expired, or journal lacks a terminal state
- **THEN** startup recovery reconciles fail-closed and appends an `ABORTED/BLOCKED` recovery record
- **AND** only then releases the lease
- **AND** an unreconcilable orphan blocks every new Design run

### Requirement: Lease guarantees are limited to the same OpenCode process

While a lease is active, the guard SHALL deny every unenumerated native/custom/MCP tool in the same OpenCode process. It SHALL permit only main's single-use `design_spawn_stage` in `CREATED`, the bound author's writer, and the bound main/helper's read-only OpenSpec tool in its enumerated phase; critics and other sessions SHALL have no tools. Author and critic SHALL keep `task: deny`, and main SHALL not use Task during the lease. Candidate/canonical validation SHALL use a dedicated staging worktree and a documented human freeze to reduce out-of-process concurrency.

#### Scenario: Non-bound or unknown in-process tool is requested

- **WHEN** any non-bound session or unenumerated capability is invoked during a lease
- **THEN** the hook denies and records it
- **AND** the run is `BLOCKED`

#### Scenario: Persistent unexplained artifact difference exists

- **WHEN** baseline and final inventory differ without a complete authorized writer-call chain
- **THEN** reconciliation is `BLOCKED`
- **AND** a later authorized edit SHALL NOT erase that violation

#### Scenario: Dedicated staging freeze is absent

- **WHEN** candidate or canonical validation shares a worktree with active external automation or lacks documented freeze
- **THEN** acceptance is `BLOCKED`

### Requirement: OpenSpec read-only operations use a custom tool without Bash

`design_openspec_readonly` SHALL accept only the enum `status|instructions|validate` and schema-validated structured parameters. The plugin SHALL invoke the `deployment-manifest.json`-approved absolute OpenSpec executable using `shell: false`, structured argv, canonical cwd, and a fixed minimal environment. Every invocation SHALL record PID, PPID, absolute executable, actual digest, `build_id`, `module_instance_id`, protocol version, exit status/result, and output digest. It SHALL accept no command string, redirection, chaining, shell syntax, arbitrary flag, alternate executable, cwd, or env override. Author and critics SHALL not receive this tool.

#### Scenario: Enumerated read-only operation is valid

- **WHEN** bound main/helper supplies an allowed enum and valid structured parameters for the canonical change/cwd
- **THEN** the exact executable may run without a shell
- **AND** argv, cwd, environment, exit status, and output digest are journaled

#### Scenario: Command or process input is not enumerated

- **WHEN** a caller supplies bash, a command string, extra flag, different executable/cwd/env, or non-read-only subcommand
- **THEN** execution is denied
- **AND** the run is `BLOCKED`

### Requirement: Evidence is correlated but not workflow-authoritative

The process SHALL write owner-only hash-chained journal bytes, evidence JSON, and a sidecar under the OpenCode data directory outside artifact write paths. A CI/read-only verifier SHALL compare runtime DB session/message/part records, plugin events/journal, process/build identity, tool mappings, artifact transitions, and final artifact bytes.

Main MAY transport exact evidence bytes and digest. Reconstruction by main SHALL not be accepted by the verifier. The resulting export SHALL not itself authorize a workflow transition and SHALL not be represented as externally attested.

#### Scenario: CI verifier correlates all sources

- **WHEN** runtime DB/events, journal/sidecar, loaded build identity, and artifacts agree
- **THEN** verification may pass within the process trust boundary
- **AND** exact bytes may be exported for #555

#### Scenario: Evidence is absent, inconsistent, or reconstructed

- **WHEN** a source is missing, schema unknown, digest broken, IDs ambiguous, or reconstructed bytes substitute for recorded bytes
- **THEN** verification is `BLOCKED`
- **AND** prose or workflow status SHALL NOT override it

### Requirement: Every persistent artifact diff is explained by calls

The verifier SHALL inventory baseline and final governed paths and reconcile each persistent added, removed, or changed path against ordered writer events. Every before digest SHALL match prior state and every after digest SHALL lead to final state.

#### Scenario: Authorized chain is complete

- **WHEN** every persistent difference has a bound, ordered, digest-consistent call chain
- **THEN** artifact reconciliation passes

#### Scenario: Chain is absent or broken

- **WHEN** a path differs without a call or a before/after link is missing, reordered, or inconsistent
- **THEN** reconciliation is `BLOCKED`
- **AND** valid final prose SHALL NOT override the gap

### Requirement: Artifact authorship executes in dependency stages

The orchestrator SHALL create only the OpenSpec scaffold; use `design_openspec_readonly`; request deterministic manifests/packets; invoke only `design_spawn_stage` for bound child stages; transport exact evidence bytes; and perform only workflow actions separately authorized to main. It SHALL not use Task during a lease. It SHALL delegate normative content in dependency order: accepted `proposal.md`, then `design.md` plus `specs/**` and any enumerated prototype paths, then `tasks.md`. Main SHALL NOT draft or patch delegated normative content.

#### Scenario: Stages execute in order

- **WHEN** proposal has an accepted final digest before design/specs and design/specs have accepted final digests before tasks
- **THEN** each stage may authorize only its manifest's exact paths

#### Scenario: Stage starts early or main changes normative bytes

- **WHEN** a dependency digest is absent or runtime/diff evidence attributes delegated normative bytes to main
- **THEN** the run is `BLOCKED`
- **AND** a later child rewrite SHALL NOT erase that violation

### Requirement: Assessments return strict structured findings

Assessment A and B SHALL run in distinct child sessions created only by `design_spawn_stage`, with identical exact packet bytes, the same normative digest, zero tools, no access to each other's output, and observed Sol/high. Each SHALL return only schema-valid canonical UTF-8 JSON. Every finding SHALL contain `finding_id`, `severity` restricted to `P0|P1|P2`, `source_digest`, `summary`, and boolean `disposition_required`. The envelope SHALL contain schema version, assessment identity, lineage ID, round, source digest, and findings.

The guard SHALL preserve and hash the exact output bytes. A deterministic helper MAY parse those same bytes only after schema validation; it SHALL NOT redact, rewrite, summarize, reorder, omit, or reclassify a finding.

#### Scenario: Independent structured Assessments complete

- **WHEN** A/B sessions/messages differ, packets/digests match, no tool is called, outputs are non-empty and schema-valid, hashes match recorded parts, and Sol/high is observed
- **THEN** exact output bytes may enter deterministic synthesis

#### Scenario: Assessment output or isolation is invalid

- **WHEN** output is prose, schema-invalid, empty, hash-mismatched, shares a session, sees the other output, uses a tool, or carries a stale digest
- **THEN** synthesis SHALL NOT start
- **AND** the gate is `BLOCKED`

### Requirement: Finding lineage and resolution are mechanically enforced

Finding IDs SHALL be unique and immutable within a lineage. Before spawn, the manifest SHALL pre-assign every inherited P0/P1 finding ID to both Assessment A and Assessment B; this version SHALL NOT support variable applicability. A recheck SHALL use the same `lineage_id`, a new current `source_digest`, and structured resolutions containing the prior `finding_id`, `prior_source_digest`, current `source_digest`, and `disposition: resolved|open`. `resolved` SHALL be valid only when both A and B return structured `resolved` for the same ancestor `finding_id`, same lineage, and same new normative digest.

Every P0/P1 SHALL remain inherited and blocking until that dual resolution is valid. Omission, conflict, duplicate/unknown ID, different lineage, stale digest, author-authored disposition, or `open` from either critic SHALL win conservatively and keep it blocking.

#### Scenario: Recheck resolves an inherited finding

- **WHEN** schema-valid A and B rechecks in the same lineage cite the same ancestor finding ID and prior digest, evaluate the same new digest, and both record `resolved`
- **THEN** that inherited finding no longer blocks on its own

#### Scenario: Recheck omits or invalidly resolves a P0/P1

- **WHEN** either critic omits a P0/P1, returns `open`, conflicts, uses another lineage, cites unknown/duplicate ancestry, or carries a stale/new-digest mismatch
- **THEN** it remains open
- **AND** verdict remains `BLOCKED`

#### Scenario: Recheck introduces a new P0/P1

- **WHEN** either valid Assessment reports a new P0/P1 on the current digest
- **THEN** the new finding is added to the lineage as blocking

### Requirement: Generated critique block and verdict are deterministic

The guard SHALL calculate verdict from validated byte-preserved A/B payloads, pre-assignment, lineage, and the conservative merge. Any current or inherited P0/P1 lacking dual structured resolution SHALL produce `BLOCKED`; P2 SHALL remain listed but shall not block by severity alone.

The guard/helper SHALL emit `generated_block_bytes` containing exact A/B payload bytes, hashes, lineage/resolutions, conservative-merge result, and the guard-calculated verdict. A bound synthesis author SHALL only replace bytes between the generated markers with those supplied bytes verbatim. It SHALL not choose or edit findings, severity, disposition, ordering, omission, or verdict. The verifier SHALL require byte equality with helper output.

#### Scenario: Author inserts generated block verbatim

- **WHEN** the replacement interval exactly equals `generated_block_bytes`
- **THEN** synthesis passes byte-equality validation
- **AND** the helper-calculated verdict is retained

#### Scenario: Author changes generated content

- **WHEN** any generated byte, finding, disposition, hash, or verdict is altered, omitted, or reordered
- **THEN** synthesis is `BLOCKED`

#### Scenario: P0/P1 is unresolved

- **WHEN** deterministic lineage evaluation finds any unresolved P0/P1
- **THEN** generated verdict is `BLOCKED`

### Requirement: Normative digest excludes only generated critique evidence

`normative_digest` SHALL cover proposal bytes; design bytes with the explicit generated interval replaced by one fixed token; specs ordered by canonical path including path and bytes; and tasks bytes. Updating only the exact generated interval SHALL not change the digest. Any other byte change SHALL invalidate previous Assessments and require a new digest/recheck.

#### Scenario: Only generated evidence is replaced

- **WHEN** the author inserts exactly the helper-generated interval
- **THEN** normative digest remains unchanged

#### Scenario: Normative content changes

- **WHEN** proposal, non-generated design, spec, or tasks bytes change
- **THEN** prior A/B evidence becomes stale
- **AND** a fresh recheck for the new digest is required

### Requirement: Additional corrections require explicit human authorization

The contract SHALL record that automatic correction stopped after round 2; for #550, Alan explicitly authorized correction round 3 in chat and at `https://github.com/oalansilva/crypto/issues/550#issuecomment-5305576566`. A and B then resolved all four inherited P1 findings in round 3 and opened `A-R3-P1-001`, `B-R3-P1-001`, and `B-R3-P1-002`.

After replying `continue`, Alan authorized only the final targeted correction of those new findings at `https://github.com/oalansilva/crypto/issues/550#issuecomment-5307214677`. That decision SHALL authorize only this normative correction and its next A/B recheck in the same lineage against a new normative digest; it SHALL NOT resolve a finding, grant PASS, or approve Design. Before the recheck spawns, all three new IDs SHALL be pre-assigned to both A and B, and the conservative merge SHALL continue to apply.

#### Scenario: Human-authorized targeted correction receives a clean conservative recheck

- **WHEN** both structured rechecks validly resolve every inherited P0/P1 under the conservative rule and introduce none
- **THEN** deterministic synthesis may evaluate the remaining gates

#### Scenario: Next recheck has any P0/P1 defect

- **WHEN** any P0/P1 is new, inherited, omitted, conflicting, unknown, invalidly resolved, or `open` after the targeted correction
- **THEN** Design remains `BLOCKED` pending human decision
- **AND** no further correction starts without another explicit human decision

### Requirement: Activation uses a quiescent process cutover

Candidate validation SHALL occur in a separate OpenCode process and dedicated candidate worktree. Canonical promotion SHALL block new Design runs, close or abort every lease, stop OpenCode, apply one complete commit/build with its matching external `deployment-manifest.json`, copy the candidate-validated profile body bytes unchanged to canonical profile names, disable candidate names in that build, validate schema/config/build plus `build_id` and `deployment_manifest_sha256` offline, start a new process, record process identity/loaded build digest, and execute the full canonical matrix in sessions created by that process. It SHALL NOT claim an atomic filesystem transaction.

#### Scenario: Candidate and canonical builds pass

- **WHEN** candidate passes separately and canonical cutover completes with no active lease, one coherent build/deployment-manifest pair, offline checks, a new process, and a green full matrix
- **THEN** technical activation may pass subject to human workflow gates

#### Scenario: Cutover is partial or process is reused

- **WHEN** runs are not blocked, a lease remains active, OpenCode is not stopped, profile bodies change, candidate aliases remain enabled, the build/deployment manifest is partial or mismatched, checks fail, or sessions use the old process/module
- **THEN** activation is `BLOCKED`

### Requirement: Rollback is quiescent and fail-closed

Rollback SHALL block runs, finalize/abort leases, stop OpenCode, restore the prior complete commit/build and matching deployment manifest, validate them offline, and start another process. It SHALL preserve journals and keep all affected Design gates `BLOCKED`. It SHALL not enable model fallback.

#### Scenario: Activation is rolled back

- **WHEN** candidate or canonical acceptance fails
- **THEN** rollback occurs only with the process stopped and leases terminal
- **AND** later activation requires the complete candidate/canonical procedure again

### Requirement: Transitional bootstrap for card 550 is honest and limited

For this Design correction, the current planner SHALL be recorded as exact `openai/gpt-5.6-sol` with provider option `reasoningEffort: high`, while runtime variant `high` remains unproven and was observed as default. The transitional exception MAY permit review under the current Design rule but SHALL NOT count as technical acceptance or authorize runtime configuration in this change round.

Separate no-mutation critics MAY provide review handles. Historical Git before/after was completed with identical hashes: `proposal.md` `de8a7bee...`, pre-recheck design `c1a74c93...`, and spec `9a4f870f...`; zero critic edits occurred. Those hashes prove only that earlier round: correction round 3 changed design/spec, and this final targeted correction changes normative bytes again and requires a new digest/recheck. After implementation, an independent fixture SHALL prove runtime variant `high` for candidates and canonical aliases in new processes.

#### Scenario: Transitional Design review is recorded accurately

- **WHEN** #550 Design artifacts are reviewed under the transitional rule
- **THEN** model/provider option and unproven/default variant are recorded separately
- **AND** Design remains `BLOCKED` until the next targeted-correction recheck and its Git verification complete

#### Scenario: Bootstrap is offered as runtime acceptance

- **WHEN** current #550 authorship, provider config, critic assertion, or file hash is used instead of the independent fixture
- **THEN** technical acceptance is `BLOCKED`

#### Scenario: Prior Git evidence is reused for the new digest

- **WHEN** the prior identical hashes are offered as mutation evidence for the next targeted-correction recheck
- **THEN** the Design review SHALL NOT pass

### Requirement: Empty or incomplete delegation fails closed

Every delegated stage SHALL have a child session, at least one message and usable recorded part, required artifact digests, and complete correlation. Empty spawn, denial, crash, creation error, missing artifact, unknown actor, output mismatch, or model/variant mismatch SHALL abort without fallback.

#### Scenario: Delegation has no usable result

- **WHEN** child/message/usable part is absent or creation fails
- **THEN** lease recovery finalizes `ABORTED/BLOCKED`
- **AND** releases the lease only after terminal evidence is durable

#### Scenario: Required evidence is missing

- **WHEN** an artifact, binding, call chain, process fact, output, or runtime record is absent
- **THEN** validation or publication SHALL NOT convert the run to PASS

### Requirement: Complete positive and negative contract tests

The implementation SHALL test all artifact stages; `design_spawn_stage` as the only lease spawn; preallocated `input_message_id` passed in SDK create/prompt correlation; exact input `chat.message.messageID`; complete packet bytes and actual input-message-part hashes; adapter-tested `ToolContext.messageID` as `assistant_message_id`; runtime `AssistantMessage.sessionID` and `parentID`; call/operation-nonce mapping before filesystem; zero-tool critic output-parent correlation; single-flight behavior; Linux helper probe and safe writes; lease state/recovery; independent pre-build `build_id`, post-build `deployment-manifest.json`/`deployment_manifest_sha256`, real-byte matching, and complete TCB identity/results; read-only custom tool/runner; two zero-tool structured critics; dual pre-assignment and conservative lineage merge; generated-block byte equality; guard-calculated verdict; CI correlation; candidate process; quiescent canonical cutover; and quiescent rollback. It SHALL exercise the corresponding fail-closed scenarios, not treat voluntary non-use as denial evidence.

#### Scenario: Positive matrix passes

- **WHEN** all positive assertions pass for candidates and then canonical names in distinct new processes
- **THEN** technical acceptance may pass subject to Design and human approval gates

#### Scenario: Negative condition is injected

- **WHEN** any prohibited, stale, ambiguous, unsafe, orphaned, reconstructed, or incomplete condition from this specification is exercised
- **THEN** tests assert mechanical denial or fail-closed recovery, evidence reference, and `BLOCKED`

### Requirement: Scope preservation

#550 SHALL leave general plugins, default Flash/Pro selection, Hermes routing, `/opsx:apply`, `/opsx:verify`, workflow DB, and #555 unchanged. In-scope implementation SHALL be limited to dedicated Design profiles, the dedicated guard, custom writer/spawn/read-only OpenSpec tools, native writer helper, read-only runner/adapter, schema/evidence, and direct tests.

#### Scenario: Scope regression is inspected

- **WHEN** implementation diff is reviewed
- **THEN** only enumerated dedicated contract files are accepted
- **AND** a change to a general plugin, defaults, Hermes, apply/verify, workflow DB, or #555 keeps the card `BLOCKED`

### Requirement: UI remains unaffected

The change SHALL introduce no product UI surface, component, route, or interaction. Prototype and browser validation SHALL remain N/A without bypassing Design or human approval.

#### Scenario: Design classifies UI impact

- **WHEN** #550 is reviewed in Design
- **THEN** it records `UI impact: none` with an infrastructure justification
- **AND** still requires `Design -> Aprovação de Design -> Pronto para Dev`
