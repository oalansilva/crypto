## MODIFIED Requirements

### Requirement: Evidence availability is checked before dependent work
The Codex adapter SHALL check the active host/session evidence capability before spawning stage work and before moving the card into a stage that depends on that work. The check MUST verify usable authoritative sources, supported schema and observed surface, recorded runtime version, identity correlation and the evidence output path. Capability qualification SHALL be discovered and revalidated by surface and driver schema independently of the current worktree's private output directory. Context qualification MUST remain bound to the current chat, root, native binary and contract scope. Unknown or unavailable capability MUST visibly refuse without spawning work, changing Status or damaging existing artifacts. A successful preflight MUST NOT count as proof of a future execution.

#### Scenario: Missing source before transition
- **WHEN** a Codex stage requires runtime evidence but its source is absent or unreadable
- **THEN** preflight reports the cause and recovery before any dependent transition or child work
- **AND** Status and existing artifacts remain unchanged

#### Scenario: Already in the stage
- **WHEN** the card is already in Design and the next author or critic is requested
- **THEN** evidence capability is rechecked before that birth, including the active session, surface, schema and recorded host/version

#### Scenario: Unsupported host qualification
- **WHEN** a surface and driver schema lack real qualification evidence
- **THEN** ordinary stage work is refused as unverified
- **AND** an explicit qualification essay may exercise collection without product work or a card transition and without relaxing existing permissions

#### Scenario: Compatible runtime version changes
- **WHEN** the runtime version changes but the observed surface and supported schema remain compatible
- **THEN** version alone does not invalidate capability qualification
- **AND** changed native binary or contextual contract still requires its own current-scope verification

#### Scenario: Reusable capability does not transfer context
- **WHEN** an intact capability proof is found from another worktree or session of the same surface and schema
- **THEN** its original sources are revalidated for capability only
- **AND** it cannot supply context qualification, births or product execution proof for the active chat/root

## ADDED Requirements

### Requirement: Qualification discovery uses private verifiable references
Qualification discovery SHALL use a private account-local index keyed by observed surface and driver schema and SHALL support verified legacy source references. The index MUST be a locator only; consumers MUST reopen immutable original proofs and authoritative sources before acceptance. Discovery MUST reject ambiguous, altered or inaccessible sources visibly, MUST NOT choose by latest timestamp alone and MUST NOT create qualification by copying receipts into the current worktree. Private shared storage MUST have restricted permissions, atomic updates and destination validation independent from the existing worktree-contained evidence writer.

#### Scenario: Valid legacy proof is discovered
- **WHEN** a new session has no worktree-local qualification and an indexed legacy proof matches its surface/schema
- **THEN** preflight revalidates that original proof and records its provenance without rewriting the original birth or sources
- **AND** current-context and stage gates still run

#### Scenario: Indexed proof was altered or removed
- **WHEN** the locator exists but any required proof or authoritative source is changed, missing or ambiguous
- **THEN** discovery reports the specific failure and does not accept the index's success label
- **AND** authorized recovery preserves the original failure and artifacts

#### Scenario: Proof from another surface
- **WHEN** an exec qualification is available for an unqualified TUI session or the converse
- **THEN** it is not accepted as that session's capability qualification
- **AND** the workflow conducts only the authorized diagnostic for the required surface or reports the missing authorization
