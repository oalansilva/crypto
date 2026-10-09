## ADDED Requirements

### Requirement: Codex local detector uses the same Impeccable trigger
The Codex local adapter SHALL pass normalized file-edit `PostToolUse` and turn `Stop` events to the existing project-local Impeccable `hook.mjs`. For the same edited UI path and session state, the detector's eligibility decision and finding class SHALL match the existing Cursor, Grok, OpenCode, and dsh adapters. A clean/non-UI edit MUST NOT spuriously trigger a UI finding. The detector SHALL remain advisory and MUST NOT convert its finding into a Guard deny or claim coverage of hosted/unhooked operations.

#### Scenario: Matching UI edit triggers consistently
- **WHEN** the same UI file edit fixture is delivered to all five adapters
- **THEN** each normalizes it to `PostToolUse` with the same `file_path`
- **AND** the shared detector reports the same eligibility and finding class

#### Scenario: Non-UI edit stays outside the detector
- **WHEN** the same non-UI path is edited in Codex CLI or IDE local
- **THEN** the detector does not emit a UI finding
- **AND** it does not block the turn

#### Scenario: Stop deep pass uses the same session set
- **WHEN** a Codex turn stops after UI files were edited
- **THEN** the shared detector receives a `Stop` event for its session-scoped deep pass
- **AND** any finding is advisory, deduplicated by the existing detector behavior
