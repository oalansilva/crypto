## ADDED Requirements

### Requirement: Evidence availability is checked before dependent work
The Codex adapter SHALL check the active host/session evidence capability before spawning stage work and before moving the card into a stage that depends on that work. The check MUST verify usable authoritative sources, supported schema and host/version, identity correlation and the evidence output path. Unknown or unavailable capability MUST visibly refuse without spawning work, changing Status or damaging existing artifacts. A successful preflight MUST NOT count as proof of a future execution.

#### Scenario: Missing source before transition
- **WHEN** a Codex stage requires runtime evidence but its source is absent or unreadable
- **THEN** preflight reports the cause and recovery before any dependent transition or child work
- **AND** Status and existing artifacts remain unchanged

#### Scenario: Already in the stage
- **WHEN** the card is already in Design and the next author or critic is requested
- **THEN** evidence capability is rechecked before that birth, including the active session and host/version

#### Scenario: Unsupported host qualification
- **WHEN** a host/version lacks real qualification evidence
- **THEN** ordinary stage work is refused as unverified
- **AND** an explicit qualification essay may exercise collection without product work or a card transition and without relaxing existing permissions

### Requirement: Observations are automatically collected from the correct runtime
For a supported execution the adapter SHALL collect observed model, effort, host/version, agent and execution identity, terminal result and returned payload evidence automatically. Requested selection MUST remain separate from observation. Each accepted observation MUST carry a verifiable source reference and integrity digest. Configuration, model catalogue, manual observed flags and the agent's own declaration MUST NOT substitute for runtime observation.

#### Scenario: Successful automatic collection
- **WHEN** a qualified runtime returns completed with payload and its corresponding events observe the captured requested model and effort
- **THEN** the adapter creates verified evidence and satisfies the runtime proof gate without manual metadata entry

#### Scenario: Requested values are the only available values
- **WHEN** runtime model or effort is missing but requested selection and a completed payload exist
- **THEN** the missing observation remains unavailable and the execution is explicitly refused

#### Scenario: Installed binary differs from active host
- **WHEN** a local binary reports a version but the execution source cannot identify its own host/version
- **THEN** the binary version does not fill the runtime observation and proof fails visibly

### Requirement: Evidence belongs to the immutable birth and relevant turns
Evidence SHALL bind the birth capture and native spawn result to the child identity, parent identity, worktree/card and relevant turn identities. Accepted terminal events and returned content MUST belong to that same execution. Continuations MUST retain their birth capture and validate each relevant new turn. Ambiguous or conflicting sources MUST be refused; neither latest-file selection nor timestamps alone establish identity.

#### Scenario: Evidence belongs to another child or turn
- **WHEN** an otherwise matching observation or completion belongs to another child, birth or turn
- **THEN** the current execution is refused with an identity mismatch rather than accepted by model equality

#### Scenario: Selection changes after birth
- **WHEN** local selection changes while a child is running
- **THEN** that child's evidence is compared to its immutable birth capture and new independent births use the new selection

#### Scenario: Continuation differs from birth
- **WHEN** a resumed turn observes a different model or effort, or has no observation
- **THEN** the continuation cannot reuse a previous turn's success and a fresh birth is required instead of retuning the live agent

#### Scenario: Valid final turn follows a divergent work turn
- **WHEN** a multi-turn execution contains a divergent required work turn followed by a matching final turn
- **THEN** final-turn equality does not erase the divergence and the execution is refused

### Requirement: Collection failure preserves useful work and supports bounded recovery
The collector SHALL use bounded waiting for runtime completion/flush, report missing, divergent, malformed or inaccessible evidence explicitly, and preserve Status and produced artifacts on failure. Recollection of the same intact execution SHALL be idempotent. A new birth MUST NOT inherit a failed execution's proof.

#### Scenario: Source disappears after preflight
- **WHEN** work produces artifacts but the source becomes unavailable before final collection
- **THEN** the adapter refuses success with a cause and recovery path while retaining artifacts and Status

#### Scenario: Delayed evidence becomes available
- **WHEN** intact evidence for the refused attempt becomes available after a transient access or flush failure
- **THEN** recollection validates the original birth and relevant turns without duplicate proxy records

#### Scenario: Evidence cannot be recovered
- **WHEN** identity or matching observation cannot be established
- **THEN** the attempt remains refused and recovery requires a new checked birth, permitting artifacts as input without treating them as execution proof

### Requirement: Existing gates and the Codex scope remain intact
Automatic evidence SHALL feed existing Codex proxies and gate verifiers without reducing human approval, Design critique, completion/payload, sandbox or exact-diff requirements. Consumers MUST verify evidence integrity and binding rather than trusting a success flag alone. Other client adapters MUST retain their existing behavior.

#### Scenario: Review wave collects evidence after read-only work
- **WHEN** two distinct native reviewers finish with matching evidence for the same exact diff
- **THEN** the writable orchestrator records their evidence after the read-only wave
- **AND** verification still requires both roles, separate births/children, observed read-only sandbox for the spawning session and reviewers, matching diff digest, completed and payload

#### Scenario: Evidence is valid but another gate fails
- **WHEN** model proof passes but the human approval, critique, sandbox, exact diff or payload requirement fails
- **THEN** runtime collection does not authorize advancement or waive that requirement

### Requirement: Support claims require real host-specific proof
Documentation SHALL identify supported, unverified and unavailable hosts by runtime identity/version, observed capabilities, evidence source and recovery path. A support claim MUST include a real successful native execution through collection and gate consumption plus refusal evidence. Simulated tests alone MUST NOT establish support or claim universal hook coverage or Auto mode.

#### Scenario: Real successful proof and refusals
- **WHEN** the native host executes a captured child with returned content and the collector verifies its origin and observed pair through the consuming gate
- **THEN** that host/version can be documented as supported with the reproducible sanitized proof and demonstrated refusal cases

#### Scenario: Fixture tests pass for another host
- **WHEN** simulated tests pass but another host/version has no real successful evidence
- **THEN** that host/version remains unverified and is not silently included in the support claim
