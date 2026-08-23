# grill-card Delta Specification

## ADDED Requirements

### Requirement: grill-card is the Em Refinamento interview front door

The repository SHALL contain `.cursor/skills/grill-card/SKILL.md` as a regular file (not git symlink mode `120000`). The skill SHALL require `bound_card` equal to the GitHub issue id and Project 1 `Status=Em Refinamento` before editing that issue. Frontmatter SHALL set `disable-model-invocation: false`. The skill SHALL instruct the agent to apply the vendored `grilling` primitive (design tree, frontier rounds, recommended answers, facts via tools, decisions from Alan). It SHALL instruct the agent to write the DoD sections into the issue body in pt-BR: Problema, História (Como/quero/para), Entra/não entra, Vocabulário (`_Avoid:`), critérios observáveis, Riscos. When the frontier is empty, it SHALL instruct a single canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` When the frontier is not empty, the card MUST remain in Em Refinamento and MUST NOT receive that comment.

#### Scenario: Bound card in Em Refinamento
- **WHEN** the session is bound to issue N and Project 1 Status of N is `Em Refinamento` and Alan asks to refine the story
- **THEN** the agent SHALL load `grill-card` and `grilling`
- **AND** SHALL update issue N body toward the DoD
- **AND** MUST NOT call `process_event priorizar` or `gh project item-edit` on Status

#### Scenario: Unbound or wrong column
- **WHEN** `bound_card` is unbound or Status is not `Em Refinamento`
- **THEN** the agent MUST NOT apply `grill-card` writes to an issue
- **AND** MUST NOT write `CONTEXT.md` or `docs/adr/`

#### Scenario: No Matt facade
- **WHEN** a contributor lists `.cursor/skills/`
- **THEN** there is no `grill-with-docs` skill directory as an entry point
- **AND** there is a `grilling` directory whose `SKILL.md` is a regular file

#### Scenario: Offer grill when body lacks DoD
- **WHEN** the session is bound to issue N, Status is `Em Refinamento`, the body lacks any DoD section, and Alan has not forbidden grilling
- **THEN** the agent SHALL offer or run `grill-card` on issue N
- **AND** MUST NOT treat every T0 as a mandatory grill
- **AND** MUST NOT run `grill-card` when Status is Todo or Design

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
