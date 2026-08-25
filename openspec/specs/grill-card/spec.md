# grill-card Specification

## Purpose
TBD - created by archiving change card-667-grill-card. Update Purpose after archive.
## Requirements
### Requirement: grill-card is the Em Refinamento interview front door
The repository SHALL contain `.cursor/skills/grill-card/SKILL.md` as a regular file (not git symlink mode `120000`). The skill SHALL require Project 1 `Status=Em Refinamento` and an explicit GitHub issue id in the spawn prompt (title `#<id>` or equivalent) before editing that issue. It MUST NOT require git branch `card-<id>-*` or a card worktree. Frontmatter SHALL set `disable-model-invocation: false`. The **parent** session MUST spawn an isolated `grill-card` child (same model, no parent transcript) and MUST only relay rounds: show the child's questions, collect Alan's answers, re-spawn or resume the child. The child SHALL apply the vendored `grilling` primitive and write the DoD sections into the issue body in pt-BR: Problema, História (Como/quero/para), Entra/não entra, Vocabulário (`_Avoid:`), critérios observáveis, Riscos. When the frontier is empty, the child SHALL post a single canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` When the frontier is not empty, the card MUST remain in Em Refinamento and MUST NOT receive that comment. The child MUST NOT call `process_event priorizar`.

#### Scenario: Bound card in Em Refinamento
- **WHEN** Project 1 Status of issue N is `Em Refinamento` and Alan asks to refine the story
- **THEN** the parent SHALL spawn `grill-card` / `grilling` with N in the prompt
- **AND** the child SHALL update issue N body toward the DoD
- **AND** MUST NOT call `process_event priorizar` or `gh project item-edit` on Status
- **AND** the parent MUST NOT write the issue body itself

#### Scenario: Unbound or wrong column
- **WHEN** the spawn prompt has no issue id, Status is not `Em Refinamento`, or N does not match the parent chat `#<id>`
- **THEN** the agent MUST NOT apply `grill-card` writes to an issue
- **AND** MUST NOT write `CONTEXT.md` or `docs/adr/`

#### Scenario: No Matt facade
- **WHEN** a contributor lists `.cursor/skills/`
- **THEN** there is no `grill-with-docs` skill directory as an entry point
- **AND** there is a `grilling` directory whose `SKILL.md` is a regular file

#### Scenario: Offer grill when body lacks DoD
- **WHEN** Status of issue N is `Em Refinamento`, the body lacks any DoD section, and Alan has not forbidden grilling
- **THEN** the parent SHALL offer or spawn `grill-card` on issue N (id in the prompt, even on `develop`)
- **AND** MUST NOT treat every T0 as a mandatory grill
- **AND** MUST NOT run `grill-card` when Status is Todo or Design

#### Scenario: Grill does not require a card branch
- **WHEN** `q_git` is `develop` or otherwise not `card-N-*` and Status of N is `Em Refinamento`
- **THEN** spawning the grill child with N in the prompt is allowed
- **AND** the skill MUST NOT refuse solely because the session is not on `card-N-*`

### Requirement: grill-card does not persist glossary files or OpenSpec

While executing `grill-card`, the agent MUST NOT create or update `CONTEXT.md`, `docs/adr/**`, or `openspec/changes/**`, and MUST NOT invoke `/opsx:new`, `/opsx:ff`, `/opsx:explore`, or `/opsx:apply`. The change MUST NOT dual-write `grill-card` or `grilling` to Hermes, `/srv/knowledge/hermes-second-brain/skills/`, or `~/.codex/skills/`.

#### Scenario: Refinement session stays on the issue
- **WHEN** a grill-card round completes
- **THEN** git status in the develop checkout MUST NOT show new `CONTEXT.md` or ADR files from that session
- **AND** no OpenSpec change is created from that skill

#### Scenario: No Hermes dual-write
- **WHEN** this change is applied
- **THEN** `grill-card` and `grilling` exist only under `.cursor/skills/` in this repo
- **AND** the apply MUST NOT copy those skills into Hermes or `~/.codex/skills/`

