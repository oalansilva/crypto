## MODIFIED Requirements

### Requirement: Composer destape and resume keep execução slug in the runbook
The canonical Cursor runbook `.cursor/skills/covenant-flow/SKILL.md` SHALL point at `.cursor/model-map.yaml` and SHALL state that destape, host `resume`, and follow-up of execução children MUST keep the vigente `execucao.slug` and MUST NOT accept `composer-2.5-fast` (or any other `forbid` slug) as the continuation model. If the host bills or resumes as fast, the parent MUST NOT use that run and MUST spawn anew with `model` equal to `execucao.slug`. Same-card search MUST use `generalPurpose` with that slug and MUST NOT use subagent_type `explore` when the host maps explore to fast. `fecho-lote` MUST NOT destape; auto-resume of a prior `fecho-lote` run MUST be ignored. The runbook MUST NOT hardcode `cursor-grok-4.6-high` or `composer-2.5` as the slug source. The runbook SHALL keep the literal needle `composer-2.5-fast` MUST NOT.

#### Scenario: Runbook documents fast abort on destape resume
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it tells the parent not to accept `composer-2.5-fast` after destape or resume of execução children
- **AND** it tells the parent to spawn anew with the vigente `execucao.slug` from `.cursor/model-map.yaml` instead of resuming fast

### Requirement: Release closeout documents Composer parent chat exception
The runbook SHALL state that release/lote closeout (T16 and `fecho-lote`) requires the parent chat to be the vigente `execucao` label/slug from `.cursor/model-map.yaml`, as the only exception to silence about the parent picker on bound cards. If the parent chat is not that slug, the runbook SHALL require a visible refusal and a new session on the vigente execução model. It MUST NOT tell operators to change picker on arbitrary card chats.

#### Scenario: Runbook refuses Grok parent for release
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` release section is read
- **THEN** it requires the vigente `execucao` parent chat for T16 and `fecho-lote`
- **AND** it refuses a juízo (`juizo`) parent chat for that closeout

### Requirement: Cursor Task model follows role not picker
The canonical Cursor runbook `.cursor/skills/covenant-flow/SKILL.md` SHALL stop telling every Task/subagent to inherit the parent picker. It SHALL state that the law is the Task `model` parameter on both spawn paths, with slugs read from `.cursor/model-map.yaml`. It SHALL list only the role grouping: juízo (grill-card, design-autor, design-critic, Assessment A/B) reads `juizo`; execução (Apply, QA, the two reviewers, same-card explore, fecho-lote) reads `execucao`. `composer-2.5-fast` MUST NOT be listed as a happy path. Reviewers on Grok MUST NOT be listed as a happy path of this change. Always-on `AGENTS.md` MUST NOT grow with the map. Isolation of existing children (no parent transcript, destape needles, sidecar, Q2–Q6, review ceiling 1+1) SHALL remain as already specified.

#### Scenario: Runbook names role models not inherit
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` is read
- **THEN** it tells the parent to pass Task `model` from `.cursor/model-map.yaml` per juízo/execução group
- **AND** it MUST NOT say that isolated children inherit the picker
- **AND** it MUST NOT embed juízo/execução slugs as the map
- **AND** `AGENTS.md` does not contain the role table or the map file body

### Requirement: Review stance lives in local reviewers not BUGBOT.md
The product SHALL version `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` with `readonly` and a YAML `model` pin equal to the vigente `execucao.slug` from `.cursor/model-map.yaml`. Review constraints SHALL live in those files. `REVIEW.md` MAY exist in a consumer and MUST NOT mention Bugbot. The product MUST NOT ship `.cursor/BUGBOT.md` or nested homonyms and MUST NOT use Cursor Bugbot (`/review-bugbot`) as Code Review. Code Review gate SHALL be `diff-reviewer` plus `code-reviewer`. `/review-security` MAY run when Alan explicitly asks. The YAML `model` is a redundant pin; Cursor Code Review spawns SHALL pass `model` equal to `execucao.slug` on both spawn paths.

#### Scenario: Product has no BUGBOT.md
- **WHEN** the product tree and a uniquely pinned Cripto tree are listed
- **THEN** no `BUGBOT.md` exists (root or nested)
- **AND** `diff-reviewer.md` and `code-reviewer.md` exist with `readonly: true` and `model` equal to `execucao.slug` from `.cursor/model-map.yaml`

#### Scenario: Optional REVIEW.md has no Bugbot
- **WHEN** a consumer adds `REVIEW.md`
- **THEN** that file does not mention Bugbot
- **AND** Code Review gate remains the two local reviewers
- **AND** `/review-security` MAY run only when Alan explicitly asks
