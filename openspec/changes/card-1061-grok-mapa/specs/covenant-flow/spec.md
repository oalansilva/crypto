## MODIFIED Requirements

### Requirement: Cursor Task model follows role not picker
The canonical Cursor runbook `.cursor/skills/covenant-flow/SKILL.md` SHALL stop telling every Task/subagent to inherit the parent picker. It SHALL state that the law is the spawn `model` parameter, with slugs read from `.cursor/model-map.yaml`. On Cursor, juízo (grill-card, design-autor, design-critic, Assessment A/B) reads top-level `juizo` and execução (Apply, QA, the two reviewers, same-card explore, fecho-lote) reads top-level `execucao`, passed as the Task `model` on both spawn paths. On Grok Build, the same groups read `juizo.grok` and `execucao.grok` and the parent passes that slug as `spawn_subagent` `model`. The Grok parent MUST NOT omit `model` and MUST NOT inherit the picker. `composer-2.5-fast` MUST NOT be listed as a happy path. The exact sentence `Revisores no Grok MUST NOT neste card` MUST NOT remain in the runbook. Reviewers on Grok MUST be listed as execução on `execucao.grok`, not as a refusal. Always-on `AGENTS.md` MUST NOT grow with the map. Isolation of existing children (no parent transcript, destape needles, sidecar, Q2–Q6, review ceiling 1+1) SHALL remain as already specified.

#### Scenario: Runbook names role models not inherit
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it tells the Cursor parent to pass Task `model` from `.cursor/model-map.yaml` per juízo/execução group
- **AND** it tells the Grok parent to pass `spawn_subagent` `model` from `juizo.grok` or `execucao.grok`
- **AND** it MUST NOT say that isolated children inherit the picker
- **AND** it MUST NOT contain `Revisores no Grok MUST NOT neste card`
- **AND** it MUST NOT embed Cursor juízo/execução slugs as the map source
- **AND** `AGENTS.md` does not contain the role table or the map file body

#### Scenario: Grok reviewers are execução in the runbook
- **WHEN** the runbook role grouping is read for Grok Build
- **THEN** `diff-reviewer` and `code-reviewer` are in the execução group that reads `execucao.grok`
- **AND** they are not listed as out of scope for Grok

### Requirement: Release closeout documents Composer parent chat exception
The runbook SHALL state that release/lote closeout (T16 and `fecho-lote`) on Cursor requires the parent chat to be the vigente top-level `execucao` label/slug from `.cursor/model-map.yaml`, as the only exception to silence about the parent picker on bound Cursor card chats. If the Cursor parent chat is not that slug, the runbook SHALL require a visible refusal and a new session on the vigente Cursor execução model. On Grok Build, the runbook SHALL state that the same closeout requires the parent chat and the `fecho-lote` child to use `execucao.grok` (`grok-4.6`), and that a parent on `juizo.grok` or any other model is a visible refusal. It MUST NOT require the Grok parent to be `composer-2.5`. It MUST NOT tell operators to change picker on arbitrary card chats.

#### Scenario: Runbook refuses a Cursor parent that is not execução
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` release section is read
- **THEN** it requires the vigente top-level `execucao` parent chat for T16 and `fecho-lote` on Cursor
- **AND** it refuses a juízo (`juizo`) parent chat for that Cursor closeout

#### Scenario: Runbook allows Grok release closeout on grok-4.6
- **WHEN** the release section is read for Grok Build
- **THEN** it requires `execucao.grok` (`grok-4.6`) for the parent chat and for `fecho-lote`
- **AND** it refuses a Grok parent on `grok-4.7` or any model other than `grok-4.6`
- **AND** it does not send that Grok closeout to another card

### Requirement: Other-client stubs keep inherit without copying the table
OpenCode and dsh skill stubs SHALL continue to map children to inherit. Grok Build skill stubs SHALL NOT map children to inherit. Each Grok stub MUST tell the agent to pass `spawn_subagent` `model` from `juizo.grok` or `execucao.grok` in `.cursor/model-map.yaml`, MUST NOT omit `model`, and MUST NOT inherit the picker. Each stub body (non-empty lines after frontmatter) MUST stay at most 8 lines and MUST NOT copy the Cursor role table. This change MUST NOT dual-write the runbook into `.grok/`, `.opencode/`, or `.dsh/`.

#### Scenario: Grok stub passes the model and stays short
- **WHEN** `.grok/skills/covenant-flow/SKILL.md` is counted excluding frontmatter
- **THEN** non-empty body lines are at most 8
- **AND** it tells the agent to pass `model` from `juizo.grok` or `execucao.grok`
- **AND** it does not map Cursor Task inherit to `spawn_subagent` inherit
- **AND** it does not list the role table

#### Scenario: OpenCode and dsh stubs still inherit
- **WHEN** OpenCode and dsh skill stubs are read
- **THEN** they still map children to inherit
- **AND** they do not copy the Grok pair or the Cursor role table

## ADDED Requirements

### Requirement: Runbook documents Grok execução resume on grok-4.6
`.cursor/skills/covenant-flow/SKILL.md` SHALL state that a Grok Build execução child resumed or followed up on a model other than `execucao.grok.slug` (`grok-4.6`), including the fast model `grok-4.7-build-fast`, does not count: the parent shows a visible failure and spawns anew with `model` `grok-4.6`. The runbook SHALL keep the literal needle `composer-2.5-fast` MUST NOT for the Cursor client. The runbook MUST NOT treat `grok-4.7-build-fast` as an accepted execução continuation.

#### Scenario: Runbook names the fast Grok resume failure
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it says a Grok execução continuation other than `grok-4.6`, including `grok-4.7-build-fast`, fails and is spawned again on `grok-4.6`
- **AND** it still contains `composer-2.5-fast` MUST NOT
