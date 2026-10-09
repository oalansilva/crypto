## MODIFIED Requirements

### Requirement: Versioned juízo/execução map file
The Cursor adapter SHALL contain `.cursor/model-map.yaml` with two bands `juizo` and `execucao` (each with top-level `label` and `slug`) and a `forbid` list that SHALL include `composer-2.5-fast` and `inherit`. Top-level Cursor pairs SHALL remain juízo `Grok 4.6` / `cursor-grok-4.6-high` and execução `Composer 2.5` / `composer-2.5`. Existing `juizo.codex` SHALL remain `GPT-6 Sol` / `gpt-6-sol` / effort `high`. Existing `execucao.codex` SHALL remain `GPT-6 Luna` / `gpt-6-luna` / effort `max`. Each band SHALL also contain a `grok` object, sibling of `codex`, with `label`, `slug`, and `effort` equal to `high`: `juizo.grok` is `Grok 4.7` / `grok-4.7` / effort `high`; `execucao.grok` is `Grok 4.6` / `grok-4.6` / effort `high`. The file SHALL NOT be a per-role map. Isolated Cursor Task children SHALL pass the top-level band slug as the Task `model` parameter on both spawn paths. The Grok Build parent SHALL pass `juizo.grok.slug` or `execucao.grok.slug` as `spawn_subagent` `model` and MUST NOT read the Cursor top-level slug or the Codex pair for that spawn. Missing file, unreadable YAML, missing `juizo`/`execucao` keys, missing or empty `juizo.grok` or `execucao.grok`, a Cursor slug listed in `forbid`, or a Grok slug the host does not accept SHALL be a visible refusal. The Grok host accepts only `grok-4.5`, `grok-4.6`, `grok-4.7`, and `grok-4.7-build-fast`. The parent MUST NOT omit `model`, MUST NOT pass `inherit`, MUST NOT inherit the picker, and MUST NOT silently substitute the Cursor slug, the Codex slug, or another host-accepted slug (including `grok-4.7-build-fast`) for the Grok pair. Codex `resolve_pair` / `pin_codex_map` MUST NOT drop or reject the `grok` sibling and MUST NOT change the Codex pairs.

#### Scenario: Map file is the slug source
- **WHEN** a Cursor parent spawns a juízo or execução child
- **THEN** it Reads `.cursor/model-map.yaml`
- **AND** the Task `model` is `juizo.slug` or `execucao.slug` according to the role group in the covenant-flow runbook
- **AND** the spawn MUST NOT use a slug from `forbid`
- **AND** the spawn MUST NOT use `juizo.grok.slug` or `execucao.grok.slug`

#### Scenario: Missing or forbidden map is refused
- **WHEN** `.cursor/model-map.yaml` is absent, unreadable, missing `juizo`/`execucao` keys, or the chosen slug is in `forbid`
- **THEN** the operator-facing chat shows a visible refusal
- **AND** the child MUST NOT run under the parent picker
- **AND** the parent MUST NOT retry with `inherit`

#### Scenario: Grok pair is present and Cursor and Codex pairs stay
- **WHEN** `.cursor/model-map.yaml` is read after this change
- **THEN** `juizo.grok` is label `Grok 4.7`, slug `grok-4.7`, and effort `high`
- **AND** `execucao.grok` is label `Grok 4.6`, slug `grok-4.6`, and effort `high`
- **AND** top-level `juizo.slug` remains `cursor-grok-4.6-high` and top-level `execucao.slug` remains `composer-2.5`
- **AND** `juizo.codex` remains `gpt-6-sol` with effort `high` and `execucao.codex` remains `gpt-6-luna` with effort `max`

#### Scenario: Missing Grok pair is a visible refusal
- **WHEN** a Grok Build parent would spawn a juízo or execução child and `juizo.grok` or `execucao.grok` is missing or has an empty slug
- **THEN** the operator-facing chat shows a visible refusal
- **AND** the parent MUST NOT omit `model`, inherit the picker, or substitute the Cursor or Codex slug

### Requirement: Role models by juízo and execução
On the Cursor client, isolated Task children SHALL use the role model passed as the Task `model` parameter on both spawn paths (named `subagent_type` or `generalPurpose` with the agent-file body pasted). They MUST NOT inherit the parent chat picker. Juízo (grill-card, Design-autor, Design-critic, Assessment A/B) SHALL use the `juizo.slug` of `.cursor/model-map.yaml`. Execução (Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card explore/search, fecho-lote) SHALL use the `execucao.slug` of that file. Slugs listed in `forbid` (including `composer-2.5-fast` and `inherit`) MUST NOT be used. On the Grok Build client, the same juízo group SHALL use `juizo.grok.slug` and the same execução group SHALL use `execucao.grok.slug`, passed as `spawn_subagent` `model`. The Grok parent MUST NOT omit `model` and MUST NOT inherit the picker. Reviewers on Grok SHALL be spawned as execução on `execucao.grok`. The sentence that reviewers on Grok MUST NOT be used MUST NOT remain operative. The git MUST NOT force the parent picker; the runbook MUST NOT recommend a picker to the parent. OpenCode and dsh children SHALL keep inherit. Grok Build children MUST NOT keep inherit. The law is the spawn parameter plus the map file; agent-file YAML `model` is a redundant pin equal to the Cursor `execucao.slug`.

#### Scenario: Juízo spawn asks for the map juizo slug
- **WHEN** the session spawns grill-card, Design-autor, Design-critic, or Assessment A/B on Cursor
- **THEN** the Task `model` is the `juizo.slug` from `.cursor/model-map.yaml`
- **AND** the child MUST NOT inherit the parent picker

#### Scenario: Execução spawn asks for the map execucao slug
- **WHEN** the session spawns Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card explore, or fecho-lote on Cursor
- **THEN** the Task `model` is the `execucao.slug` from `.cursor/model-map.yaml`
- **AND** it MUST NOT require a slug from `forbid`
- **AND** it MUST NOT use `juizo.grok` or `execucao.grok` for those Cursor roles

#### Scenario: Grok juízo reads juizo.grok
- **WHEN** a Grok Build parent spawns grill-card, Design-autor, Design-critic, or Assessment A/B
- **THEN** `spawn_subagent` `model` is `juizo.grok.slug` (`grok-4.7`)
- **AND** the spawn MUST NOT omit `model` or inherit the picker

#### Scenario: Grok execução reads execucao.grok
- **WHEN** a Grok Build parent spawns Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card explore, or fecho-lote
- **THEN** `spawn_subagent` `model` is `execucao.grok.slug` (`grok-4.6`)
- **AND** the spawn MUST NOT omit `model` or inherit the picker

#### Scenario: OpenCode and dsh keep inherit
- **WHEN** OpenCode or dsh stubs are read
- **THEN** they still map children to inherit
- **AND** they MUST NOT copy the Cursor role table or `.cursor/model-map.yaml`
- **AND** Grok stubs MUST NOT map children to inherit

### Requirement: Release and lote closeout require Composer parent chat
When the operator explicitly asks to close the lote, subir a release, or run T16 (`process_event fechar_release`), including the isolated `fecho-lote` kaizen child, the Cursor parent chat MUST use the `execucao.slug` from `.cursor/model-map.yaml`. This is the sole exception to silence about the parent picker on bound Cursor card chats. If the Cursor parent chat is the `juizo.slug` or any model other than `execucao.slug`, the parent SHALL refuse visibly: it MUST NOT run T16 or spawn `fecho-lote` in that chat and SHALL direct the operator to a new session with the vigente Cursor `execucao` label/slug. On Grok Build, the same closeout MUST use `execucao.grok` (`grok-4.6`) for the parent chat and for the `fecho-lote` child `model`. A Grok parent on `juizo.grok` (`grok-4.7`) or any model other than `grok-4.6` SHALL refuse visibly and MUST NOT run T16 or spawn `fecho-lote` in that chat. Grok closeout MUST NOT require `composer-2.5`. This Grok closeout is in scope of this card. Juízo remains only for juízo roles in the runbook grouping. The git MUST NOT force the parent picker via `AGENTS.md`, harness, or overlay `clients.*.auto`. The runbook MUST NOT recommend a parent picker on other `#<id>` card chats.

#### Scenario: Cursor parent that is not execução refuses T16
- **WHEN** the operator asks to fechar o lote or subir a release on Cursor while the parent chat is not the `execucao.slug` from `.cursor/model-map.yaml`
- **THEN** the parent shows a visible refusal
- **AND** it MUST NOT call `process_event fechar_release` in that chat
- **AND** it MUST NOT spawn `fecho-lote` in that chat

#### Scenario: Composer parent may run release closeout
- **WHEN** the operator asks to fechar o lote or subir a release and the Cursor parent chat is the `execucao.slug` from `.cursor/model-map.yaml`
- **THEN** the parent MAY spawn `fecho-lote` and call T16 per the existing closeout contract
- **AND** that Cursor child MUST NOT use `grok-4.6`

#### Scenario: Grok parent on grok-4.6 may close the release
- **WHEN** the operator asks to fechar o lote or subir a release on Grok Build and the parent chat is `execucao.grok.slug` (`grok-4.6`)
- **THEN** the parent MAY spawn `fecho-lote` with `model` `grok-4.6` and call T16 per the existing closeout contract
- **AND** it MUST NOT require the parent to be `composer-2.5`

#### Scenario: Grok juízo parent refuses T16
- **WHEN** the operator asks to fechar o lote or subir a release on Grok Build and the parent chat is `juizo.grok.slug` (`grok-4.7`) or any model other than `grok-4.6`
- **THEN** the parent shows a visible refusal
- **AND** it MUST NOT call `process_event fechar_release` in that chat
- **AND** it MUST NOT spawn `fecho-lote` in that chat

### Requirement: Code Review happy path MUST use Composer execução model
On the Cursor client, the versioned `diff-reviewer` and `code-reviewer` Tasks MUST use the `execucao.slug` from `.cursor/model-map.yaml` on both spawn paths (named `subagent_type` or `generalPurpose` with the agent-file body). They MUST NOT inherit the parent picker and MUST NOT use `juizo.grok.slug`, `execucao.grok.slug`, or a slug from `forbid`. On the Grok Build client, the same two reviewers MUST be spawned and MUST use `execucao.grok.slug` (`grok-4.6`). They MUST NOT be refused as out of scope. They MUST NOT inherit the picker and MUST NOT omit `model`. Cursor Bugbot (`/review-bugbot`) MUST NOT be part of the product or the Code Review happy path. `/review-security` MAY run when Alan explicitly asks; it MUST NOT replace the local reviewers as the gate. Review constraints SHALL live in the two agent files (and optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`. Agent-file YAML MAY pin `model` equal to the Cursor `execucao.slug`; the law remains the spawn parameter plus the map file. That YAML pin MUST NOT be changed to `grok-4.6`.

#### Scenario: Local reviewers use Composer execução
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md` on Cursor
- **THEN** the child MUST use the `execucao.slug` from `.cursor/model-map.yaml`
- **AND** the spawn MUST NOT omit `model` or pass `inherit`
- **AND** the spawn MUST NOT use `grok-4.6`

#### Scenario: Grok reviewers are born on grok-4.6
- **WHEN** Code Review on Grok Build spawns `diff-reviewer` and `code-reviewer`
- **THEN** each `spawn_subagent` `model` is `execucao.grok.slug` (`grok-4.6`)
- **AND** the spawn MUST NOT omit `model` or inherit the picker
- **AND** the runbook sentence `Revisores no Grok MUST NOT neste card` is not operative

#### Scenario: Bugbot is not a product path
- **WHEN** Code Review runs on a pinned consumer
- **THEN** `/review-bugbot` MUST NOT run as the gate
- **AND** `BUGBOT.md` MUST NOT be required

## ADDED Requirements

### Requirement: Grok execução resume outside grok-4.6 does not count
When a Grok Build parent resumes or follows up an isolated execução child (Apply-coluna, QA, `diff-reviewer`, `code-reviewer`, same-card search, `fecho-lote`) on a model other than `execucao.grok.slug` (`grok-4.6`), including `grok-4.7-build-fast`, that run MUST NOT count. The parent SHALL show a visible failure and MUST NOT accept that run. The parent SHALL spawn a new child with `model` equal to `grok-4.6` and a self-contained prompt. This applies the already vigente resume law to the Grok pair Alan closed. It MUST NOT add `grok-4.7-build-fast` as the only forbidden token in place of equality with `grok-4.6`. The Cursor rule for `composer-2.5-fast` MUST remain.

#### Scenario: Fast resume of a Grok execução child fails and is respawned
- **WHEN** an execução child on Grok Build is resumed or followed up as `grok-4.7-build-fast` or any model other than `grok-4.6`
- **THEN** the parent MUST NOT treat that continuation as the passing child
- **AND** the parent spawns a new child with `model` `grok-4.6`
- **AND** the chat shows a visible failure for the rejected continuation

#### Scenario: Resume on grok-4.6 counts
- **WHEN** an execução child on Grok Build continues on `grok-4.6`
- **THEN** the parent MAY accept that continuation
- **AND** it MUST NOT replace it with `grok-4.7` or `grok-4.7-build-fast`
