## MODIFIED Requirements

### Requirement: Independent critics MUST use juízo Grok 4.6 model
Assessment A and Assessment B MUST run in isolated subagents using Grok 4.6 (`cursor-grok-4.6-high`), the same juízo identifier as the Design-autor child. They MUST receive a self-contained prompt and MUST NOT inherit the parent transcript. They MUST NOT inherit the parent chat picker. They MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype files, or product code. Isolation is process (no shared transcript, instruction not to edit product), not a plugin. Model equality SHALL be between Design-autor and A/B, not between A/B and the parent picker.

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with subagent support available
- **THEN** Assessment A MUST review product/UX/heuristics and Assessment B MUST review detector/browser evidence in separate contexts
- **AND** both subagents MUST report Grok 4.6 (`cursor-grok-4.6-high`) before synthesis
- **AND** neither spawn includes the parent Design transcript
- **AND** neither spawn inherits the parent picker

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot enforce or observe the juízo model on A/B or cannot provide the required subagent contexts
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no silent inherit of the parent picker and no silent degraded `PASS` MAY be used

#### Scenario: Critic return is bullets plus snapshot
- **WHEN** Assessment A or B finishes
- **THEN** the return to the parent is P0–P3 bullets, disposition, verdict, and snapshot path
- **AND** the full rubric dump lives in `.impeccable/critique/`, not in the parent chat
