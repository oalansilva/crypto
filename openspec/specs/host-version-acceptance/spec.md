# host-version-acceptance Specification

## Purpose
TBD - created by archiving change card-1101-claude-code-adapter. Update Purpose after archive.
## Requirements
### Requirement: Host updates do not block the process when the evidence format is unchanged
Every runtime-evidence collector (Claude Code `claude-transcript-v1`, Codex rollout driver) SHALL accept any host version whose source records match the driver's declared schema, instead of a fixed list of qualified versions. The schema SHALL declare, per record kind the collector uses, the required fields and types; unknown extra fields and unused record kinds MUST be ignored. A record the collector needs that lacks a required field or has a different type MUST refuse with `unsupported_schema` naming the record kind, the field and the observed host version. The observed host version SHALL be recorded in the receipt and evidence and MUST NOT by itself refuse preparation, collection, a spawn or a transition. Qualification and rehearsals SHALL be per driver schema, not per host version. Capability floors that only refuse older hosts lacking a required capability (for example per-invocation effort) SHALL remain. Host type and surface checks are not version checks and SHALL remain. Real observed model and effort remain mandatory: evidence that is missing or diverges from the capture MUST fail the gate in every host version.

#### Scenario: Auto-updated host with the same format
- **WHEN** the host updated itself to a version never seen before and its records match the schema
- **THEN** `prepare` returns ready, the child is born, and the evidence records the new host version

#### Scenario: Format really changed
- **WHEN** a record the collector needs lacks the model or effort field in a new host version
- **THEN** preparation or collection stops with `unsupported_schema` naming the field and version, before any dependent birth or transition

#### Scenario: Evidence diverges in any version
- **WHEN** the observed model or effort differs from the capture, or the evidence is missing, in a host version whose format matches
- **THEN** the dependent gate is refused visibly

#### Scenario: Codex update with the same rollout format
- **WHEN** Codex CLI is updated to a new version whose rollout records match the driver schema
- **THEN** the Codex preflight accepts the session without a new driver or code change, and the qualification of the driver schema stays valid

#### Scenario: Older host below a capability floor
- **WHEN** the Claude Code host is older than the per-invocation effort floor
- **THEN** the resolver refuses with `capability_unavailable`, while every newer version is not refused by its number

