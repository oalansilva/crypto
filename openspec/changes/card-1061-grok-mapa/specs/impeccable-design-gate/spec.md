## MODIFIED Requirements

### Requirement: Independent critics MUST use juízo Grok 4.6 model
On Cursor, Assessment A and Assessment B MUST run in isolated subagents using the `juizo.slug` from `.cursor/model-map.yaml` (Cursor juízo label Grok 4.6, slug `cursor-grok-4.6-high`), the same juízo identifier as the Cursor Design-autor child. On Grok Build, Assessment A and Assessment B MUST use `juizo.grok.slug` (`grok-4.7`), the same juízo identifier as the Grok Design-autor, and MUST NOT use the Cursor slug or the parent picker. They MUST receive a self-contained prompt and MUST NOT inherit the parent transcript. They MUST NOT inherit the parent chat picker. The Grok spawn MUST NOT omit `model`. They MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype files, or product code. Isolation is process (no shared transcript, instruction not to edit product), not a plugin. Model equality SHALL be between Design-autor and A/B on that client, not between A/B and the parent picker. This card is sem-tela and MUST NOT run the Impeccable pipeline.

#### Scenario: Same-model dual critique
- **WHEN** the Impeccable critique is executed with subagent support available on Cursor
- **THEN** Assessment A MUST review product/UX/heuristics and Assessment B MUST review detector/browser evidence in separate contexts
- **AND** both subagents MUST report the vigente Cursor `juizo` label/slug from `.cursor/model-map.yaml` before synthesis
- **AND** neither spawn includes the parent Design transcript
- **AND** neither spawn inherits the parent picker

#### Scenario: Grok A/B use juizo.grok
- **WHEN** a later Grok Build card runs Assessment A and Assessment B
- **THEN** both use `juizo.grok.slug` (`grok-4.7`)
- **AND** neither uses `cursor-grok-4.6-high` or inherits the picker
- **AND** this sem-tela card does not spawn A/B

#### Scenario: Model equality cannot be proven
- **WHEN** the orchestrator cannot enforce or observe the juízo model on A/B or cannot provide the required subagent contexts
- **THEN** the Design verdict MUST be `BLOCKED`
- **AND** no silent inherit of the parent picker and no silent degraded `PASS` MAY be used

#### Scenario: Critic return is bullets plus snapshot
- **WHEN** Assessment A or B finishes
- **THEN** the return to the parent is P0–P3 bullets, disposition, verdict, and snapshot path
- **AND** the full rubric dump lives in `.impeccable/critique/`, not in the parent chat
