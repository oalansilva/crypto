# grill-card Specification

## Purpose
Em Refinamento grelha a história no body do GitHub issue (`grill-card` + vendor `grilling`). Q fechada lista todas as alternativas no card da ferramenta do host; o pai relaying não colapsa à recomendada.
## Requirements
### Requirement: grill-card is the Em Refinamento interview front door
The repository SHALL contain `.cursor/skills/grill-card/SKILL.md` as a regular file (not git symlink mode `120000`). The skill SHALL require Project 1 `Status=Em Refinamento` and an explicit GitHub issue id in the spawn prompt (title `#<id>` or equivalent) before editing that issue. It MUST NOT require git branch `card-<id>-*` or a card worktree. Frontmatter SHALL set `disable-model-invocation: false`. The **parent** session MUST spawn an isolated `grill-card` child (same model, no parent transcript) and MUST only relay rounds: present every closed question with **all** alternatives the child listed, collect Alan's answers, re-spawn or resume the child. The parent MUST NOT collapse a closed question to the recommended option alone. The child SHALL apply the vendored `grilling` primitive and write the DoD sections into the issue body in pt-BR: Problema, História (Como/quero/para), Entra/não entra, Vocabulário (`_Avoid:`), critérios observáveis, Riscos. When the frontier is empty, the child SHALL ensure exactly one canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` exists on the issue: if an existing comment is already that exact text, leave it; if an existing canonical grill-card comment has the wrong text, edit or minimize that comment; MUST NOT post a second copy. When the frontier is not empty, the card MUST remain in Em Refinamento and MUST NOT receive a new copy of that comment. The child MUST NOT call `process_event priorizar`.

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

#### Scenario: Canonical comment already exact
- **WHEN** the frontier becomes empty and issue N already has a comment whose body is exactly `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **THEN** the child MUST leave that comment
- **AND** MUST NOT post another

#### Scenario: Frontier reopens after canonical comment
- **WHEN** the frontier is not empty and issue N already has the canonical comment from a previous empty frontier
- **THEN** the child MUST NOT post a second canonical comment
- **AND** the card MUST remain in Em Refinamento

#### Scenario: Canonical comment text is wrong
- **WHEN** the frontier is empty and issue N has a grill-card canonical comment whose text is not the exact required line
- **THEN** the child SHALL edit or minimize that existing comment to the exact text
- **AND** MUST NOT create a duplicate comment

### Requirement: Closed grill questions list all host-tool options
`.cursor/skills/grill-card/SKILL.md` SHALL state the host-tool contract for both clients. A **closed** frontier question with mutually exclusive real alternatives MUST be presented with every alternative in the host tool `options[]` (Cursor `AskUserQuestion`, Grok `ask_user_question`). N SHALL be the count of those real alternatives and MUST be ≥2. The recommended alternative MUST be the first option; its label MUST include `(Recommended)`. The host automatic Other line MUST NOT count toward N and MUST NOT replace a missing alternative. A closed question MUST NOT be presented with only one option. The isolated child MUST NOT call the host tool; it SHALL return each closed question with the N options listed (labels A/B/… plus the recommendation, recommended first) so the parent can map them 1:1 into `options[]` in the same order. An **open** (free-text) question MUST be presented as markdown and/or the host Other field; the agent MUST NOT invent fake `options[]` only to make a card appear. When the host tool is unavailable, the fallback SHALL be the Matt markdown format: the **body** of a closed question lists the choices and the `➡️` line is only the recommendation (MUST NOT be only the arrow). `.cursor/skills/grilling/SKILL.md` MUST remain the Matt copy and MUST NOT name the host tools. `.grok/skills/grill-card/SKILL.md` and `.grok/skills/grilling/SKILL.md` MUST NOT name `AskUserQuestion` or `ask_user_question`.

#### Scenario: Closed question on Grok lists N options
- **WHEN** a grill round on Grok has a closed question with N mutually exclusive real alternatives
- **THEN** `ask_user_question.options[]` SHALL list those N alternatives with N≥2
- **AND** the recommended alternative SHALL be first with `(Recommended)` in the label
- **AND** the automatic Other line MUST NOT count toward N

#### Scenario: Closed question on Cursor lists N options
- **WHEN** a grill round on Cursor has a closed question with N mutually exclusive real alternatives
- **THEN** `AskUserQuestion.options[]` SHALL list those N alternatives with N≥2
- **AND** the recommended alternative SHALL be first with `(Recommended)` in the label
- **AND** presenting only 1 option is forbidden

#### Scenario: Open question has no fake options
- **WHEN** a frontier question is open (free text)
- **THEN** the presenter MUST NOT invent `options[]`
- **AND** the operator answers in markdown and/or Other

#### Scenario: Operator does not see only the recommended
- **WHEN** the operator looks at the host-tool card for a closed question on either client
- **THEN** the card MUST NOT show only 1 option (plus Other)

#### Scenario: Child dump lists options for parent mapping
- **WHEN** the isolated grill child returns a closed question
- **THEN** the return SHALL list all N real alternatives plus the recommendation (recommended first)
- **AND** MUST NOT return only the `➡️` line
- **AND** the child MUST NOT itself call `AskUserQuestion` or `ask_user_question`

#### Scenario: Markdown fallback lists choices in the body
- **WHEN** the host tool is unavailable and the round falls back to Matt markdown
- **THEN** the body of a closed question SHALL list the choices
- **AND** the `➡️` line SHALL be only the recommendation
- **AND** presenting only the arrow is forbidden

#### Scenario: Vendor Matt and Grok stubs stay intact
- **WHEN** this change is applied
- **THEN** `.cursor/skills/grilling/SKILL.md` SHALL still contain `❓` and `➡️` and MUST NOT contain `AskUserQuestion` or `ask_user_question`
- **AND** `.grok/skills/grill-card/SKILL.md` and `.grok/skills/grilling/SKILL.md` MUST NOT contain `AskUserQuestion` or `ask_user_question`
- **AND** `scripts/process-fsm/grok_stubs.py` MUST NOT be edited

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

