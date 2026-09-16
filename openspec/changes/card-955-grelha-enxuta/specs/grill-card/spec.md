## ADDED Requirements

### Requirement: Lean grill is one pass with at most five product questions
The adapter `.cursor/skills/grill-card/SKILL.md` SHALL state that a grill that runs is **exactly one** pass with at most **five** product questions. The vendored primitive `.cursor/skills/grilling/SKILL.md` MUST NOT be edited to cut the design tree. After that pass, remaining open operator decisions SHALL be listed for Design (bullets under Entra and/or the child dump to the parent). The adapter MUST NOT start a second grill pass. Host-option ritual (N≥2, every alternative, recommended first) SHALL remain unchanged.

#### Scenario: Six product questions fail the golden
- **WHEN** a child dump of a grill that ran lists more than five product questions
- **THEN** `scripts/process-fsm/test_grill_card.py` SHALL fail that dump

#### Scenario: Second pass fails the golden
- **WHEN** a child dump records a second grill pass on the same issue after the first pass returned
- **THEN** the golden SHALL fail that dump

#### Scenario: Vendor grilling stays Matt
- **WHEN** this change is applied
- **THEN** `.cursor/skills/grilling/SKILL.md` SHALL still contain `❓` and `➡️`
- **AND** MUST NOT gain the one-pass or five-question runbook

### Requirement: Body write is a section delta
When the isolated child (Cursor/Grok) or the dsh root writes the issue body, it SHALL reconstruct the body so that unchanged DoD section text remains byte-identical and SHALL rewrite only the sections that changed in this pass. GitHub REST PATCH MAY send the full body. The child dump / parent handoff SHALL list the names of the changed sections. A dump that rewrites an unchanged section SHALL fail the golden. The child MUST NOT call `gh issue view`.

#### Scenario: Unchanged section rewrite fails
- **WHEN** a fixture dump rewrites a DoD section whose text did not change in that pass
- **THEN** `scripts/process-fsm/test_grill_card.py` SHALL fail that dump

#### Scenario: Handoff lists the delta
- **WHEN** a grill pass changes only Entra
- **THEN** the child dump or parent handoff SHALL list Entra as the delta
- **AND** `.cursor/skills/grill-card/SKILL.md` SHALL contain the needles `PATCH só das seções que mudaram` and `handoff lista o delta`

### Requirement: Parent skips a nítido card
When Project 1 Status of issue N is `Em Refinamento` and the issue body already states who suffers and what entra/não entra, the **parent** MUST NOT spawn `grill-card` unless Alan explicitly asks to grelhar/afiar. The parent SHALL ensure exactly one comment whose body is `card nítido; sem grill` exists (exact text already present → leave it; MUST NOT post a second copy). That comment is not the T1 canonical grill-card comment. Pytest SHALL treat nítido as: heading `## Problema` with non-empty following text **and** heading `## Entra` or `## Não entra` with non-empty following text. `.cursor/skills/covenant-flow/SKILL.md` section `## Grill-card` SHALL contain the exact substring `card nítido; sem grill`.

#### Scenario: Nítido body does not spawn grill
- **WHEN** Status of issue N is `Em Refinamento`, the body has non-empty `## Problema` and non-empty `## Entra` or `## Não entra`, and Alan has not asked to grelhar/afiar
- **THEN** the parent MUST NOT spawn `grill-card`
- **AND** SHALL post or keep the exact comment `card nítido; sem grill`

#### Scenario: Explicit grill still runs on a nítido card
- **WHEN** Alan explicitly asks to grelhar/afiar issue N in `Em Refinamento`
- **THEN** the parent SHALL spawn `grill-card` even if the body already states who suffers and entra/não entra

#### Scenario: Skip comment is idempotent
- **WHEN** the nítido skip applies and issue N already has a comment whose body is exactly `card nítido; sem grill`
- **THEN** the parent MUST leave that comment
- **AND** MUST NOT post another

### Requirement: Empty frontier of this adapter is three DoD sections and no open operator decision
For `grill-card`, an empty frontier SHALL mean the issue body has the three DoD sections **and** no operator decision remains open. The three headings SHALL be `## Problema`, `## História`, and `## Entra` (`## Não entra` MAY exist as a sibling). Observable acceptance criteria SHALL live inside Entra. The body MUST NOT be required to contain `## Vocabulário`, `## Critérios de aceite`, or `## Riscos`. The full Matt design tree MAY continue in Design and MUST NOT be required to complete in Em Refinamento. The canonical comment text SHALL remain exactly `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Only the *when* of posting it changes. Idempotence SHALL stay: exact text already present → leave it; wrong canonical grill-card comment → edit or minimize; MUST NOT post a second copy. T1 remains Alan-only. This requirement MUST NOT add a Kanban column or change Status.

#### Scenario: Stop after three-section operator DoD
- **WHEN** the issue body has the three DoD sections and no operator decision is open
- **THEN** the child SHALL post or keep exactly one canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **AND** MUST NOT keep asking design-tree questions in Em Refinamento
- **AND** MUST NOT change the canonical comment text
- **AND** MUST NOT write `## Vocabulário` or `## Riscos` into the issue body

#### Scenario: Canonical comment text stays the pinned line
- **WHEN** this change is applied
- **THEN** `.cursor/skills/grill-card/SKILL.md` SHALL still contain the exact substring `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **AND** MUST NOT introduce a replacement T1 handoff sentence

### Requirement: Offer-grill trigger is missing who-suffers plus entra
The offer-or-spawn trigger SHALL be: Project 1 Status of issue N is `Em Refinamento` **and** the issue body does not already state who suffers and what entra/não entra (or Alan asks to grill/afiar). Cards that already state who suffers and entra/não entra are skipped by the nítido-parent requirement. The operator-language ceiling MUST NOT force a re-grill of a skipped or already-grilled card. The ceiling MUST NOT run `grill-card` when Status is Todo or Design. `/opsx:explore`, schema `grill-driven`, `grill-with-docs`, `to-spec`, and a marketplace skill MUST NOT become the Em Refinamento front door; the door remains `grill-card`.

#### Scenario: Complete lean DoD is not re-grilled by the ceiling
- **WHEN** Status of issue N is `Em Refinamento` and the body already has the three DoD sections
- **THEN** the parent MUST NOT spawn `grill-card` solely because the ceiling exists
- **AND** Alan MAY still T1 without a new grill

#### Scenario: Explore is not the Em Refinamento door
- **WHEN** someone tries `/opsx:explore`, `grill-driven`, or a marketplace skill as the Em Refinamento interview door
- **THEN** the door SHALL remain `grill-card`
- **AND** those entry points MUST NOT replace the adapter

### Requirement: Lean-grill goldens live with the adapter
`scripts/process-fsm/test_grill_card.py` SHALL cover: DoD of three sections, one pass with a ceiling of five product questions, nítido skip (Q2=A), body delta, and Design artifacts that MUST contain `## Problema` / `## História` / `## Entra` copied from the grilled issue. A `proposal.md` without those headings (or an observable equivalent) SHALL fail the golden. A fixture that copies those headings from the issue SHALL pass. Apply MUST NOT `gh issue edit` already-grilled issues to shrink their bodies. Ceiling goldens from the operator-language-ceiling requirement SHALL stay green.

#### Scenario: Three-section needles replace six
- **WHEN** pytest runs after this change
- **THEN** the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md` SHALL contain `3 seções` and `card nítido; sem grill`
- **AND** MUST NOT contain `6 seções do DoD`

#### Scenario: Proposal fixture fails if it omits the grilled story
- **WHEN** a fixture `proposal.md` lacks headings `## Problema`, `## História`, or `## Entra` (or an observable equivalent)
- **THEN** the golden SHALL fail that fixture

#### Scenario: Proposal fixture that copies the issue passes
- **WHEN** a fixture `proposal.md` copies `## Problema`, `## História`, and `## Entra` from the grilled issue
- **THEN** the golden SHALL pass that fixture

## MODIFIED Requirements

### Requirement: grill-card is the Em Refinamento interview front door
The repository SHALL contain `.cursor/skills/grill-card/SKILL.md` as a regular file (not git symlink mode `120000`). The skill SHALL require Project 1 `Status=Em Refinamento` and an explicit GitHub issue id in the spawn prompt (title `#<id>` or equivalent) before editing that issue. It MUST NOT require git branch `card-<id>-*` or a card worktree. Frontmatter SHALL set `disable-model-invocation: false`. This spawn/relay ritual applies to Cursor and Grok. The dsh runtime-root ritual is a separate requirement. On Cursor and Grok, the **parent** session MUST spawn an isolated `grill-card` child (same model, no parent transcript) and MUST only relay rounds: present every closed question with **all** alternatives the child listed, collect Alan's answers, re-spawn or resume the child. The parent MUST NOT collapse a closed question to the recommended option alone. The child SHALL apply the vendored `grilling` primitive and write the DoD sections into the issue body in pt-BR: Problema, História (Como/quero/para), Entra/não entra (observable acceptance criteria inside Entra). The child MUST NOT write `## Vocabulário` or `## Riscos` into the issue body. When the frontier is empty, the child SHALL ensure exactly one canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` exists on the issue: if an existing comment is already that exact text, leave it; if an existing canonical grill-card comment has the wrong text, edit or minimize that comment; MUST NOT post a second copy. When the frontier is not empty, the card MUST remain in Em Refinamento and MUST NOT receive a new copy of that comment. The child MUST NOT call `process_event priorizar`.

#### Scenario: Bound card in Em Refinamento
- **WHEN** the client is Cursor or Grok, Project 1 Status of issue N is `Em Refinamento` and Alan asks to refine the story
- **THEN** the parent SHALL spawn `grill-card` / `grilling` with N in the prompt
- **AND** the child SHALL update issue N body toward the DoD
- **AND** MUST NOT call `process_event priorizar` or `gh project item-edit` on Status
- **AND** the parent MUST NOT write the issue body itself

#### Scenario: dsh root does not spawn and MAY edit the body
- **WHEN** the client is dsh, Project 1 Status of issue N is `Em Refinamento` and Alan asks to refine the story
- **THEN** the runtime root MUST NOT spawn a grill-shaped `subagent` or `subagent_fork`
- **AND** the root MAY `gh issue edit` the issue body
- **AND** there is no grill child that writes the body on the root's behalf

#### Scenario: Unbound or wrong column
- **WHEN** the spawn prompt has no issue id, Status is not `Em Refinamento`, or N does not match the parent chat `#<id>`
- **THEN** the agent MUST NOT apply `grill-card` writes to an issue
- **AND** MUST NOT write `CONTEXT.md` or `docs/adr/`

#### Scenario: No Matt facade
- **WHEN** a contributor lists `.cursor/skills/`
- **THEN** there is no `grill-with-docs` skill directory as an entry point
- **AND** there is a `grilling` directory whose `SKILL.md` is a regular file

#### Scenario: Offer grill when body lacks who-suffers and entra
- **WHEN** the client is Cursor or Grok, Status of issue N is `Em Refinamento`, the body does not already state who suffers and what entra/não entra, and Alan has not forbidden grilling
- **THEN** the parent SHALL offer or spawn `grill-card` on issue N (id in the prompt, even on `develop`)
- **AND** MUST NOT treat every T0 as a mandatory grill
- **AND** MUST NOT run `grill-card` when Status is Todo or Design

#### Scenario: Grill does not require a card branch
- **WHEN** the client is Cursor or Grok, `q_git` is `develop` or otherwise not `card-N-*` and Status of N is `Em Refinamento`
- **THEN** spawning the grill child with N in the prompt is allowed
- **AND** the skill MUST NOT refuse solely because the session is not on `card-N-*`

#### Scenario: Canonical comment already exact
- **WHEN** the client is Cursor or Grok, the frontier becomes empty and issue N already has a comment whose body is exactly `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **THEN** the child MUST leave that comment
- **AND** MUST NOT post another

#### Scenario: Frontier reopens after canonical comment
- **WHEN** the client is Cursor or Grok, the frontier is not empty and issue N already has the canonical comment from a previous empty frontier
- **THEN** the child MUST NOT post a second canonical comment
- **AND** the card MUST remain in Em Refinamento

#### Scenario: Canonical comment text is wrong
- **WHEN** the client is Cursor or Grok, the frontier is empty and issue N has a grill-card canonical comment whose text is not the exact required line
- **THEN** the child SHALL edit or minimize that existing comment to the exact text
- **AND** MUST NOT create a duplicate comment

#### Scenario: Child writes three DoD sections not six
- **WHEN** a grill that runs completes an empty frontier
- **THEN** the issue body SHALL contain `## Problema`, `## História`, and `## Entra`
- **AND** MUST NOT be required to contain `## Vocabulário` or `## Riscos`

### Requirement: Operator language ceiling on every Em Refinamento card
The adapter `.cursor/skills/grill-card/SKILL.md` SHALL state a language ceiling that applies to **every** card in Project 1 `Status=Em Refinamento` (product stories such as Monitor and process/harness cards alike). Closed questions and their host-tool options MUST be in operator Portuguese: who suffers, what passes/fails, and what is out of this card. A candidate question that is intelligible only with a git identifier (function name, path, yaml flag, flow event, or hash) MUST NOT appear on the host-tool card. That content SHALL be written as a **fact** in the issue body or as *como* (mechanism) in Design (`design.md`), never as an option and never as an issue heading `## Riscos`. Entra of the grilled card SHALL describe observable behavior, not the mechanism. The vendored primitive `.cursor/skills/grilling/SKILL.md` MUST NOT be edited for this ceiling. Host-option ritual from the closed-questions requirement (N≥2, every alternative, recommended first) SHALL remain unchanged; only the **content** of questions changes.

#### Scenario: Git identifier is not a host-tool question
- **WHEN** a grill round in Em Refinamento has a candidate closed question that is intelligible only with a function name, path, yaml flag, flow event, or hash
- **THEN** that candidate MUST NOT appear on the host-tool card
- **AND** the fact SHALL go into the issue body or the *como* SHALL go to Design
- **AND** the adapter MUST NOT create `## Riscos` on the issue for that *como*

#### Scenario: Same ceiling on a product story
- **WHEN** the bound card is a product story (for example Monitor) in `Em Refinamento`
- **THEN** the same operator-language ceiling SHALL apply
- **AND** a question intelligible only with a path or component name MUST NOT appear as a host-tool option

#### Scenario: Same ceiling on a harness card
- **WHEN** the bound card is a process or harness card in `Em Refinamento`
- **THEN** the same operator-language ceiling SHALL apply
- **AND** MUST NOT be skipped because the card is about the adapter itself

#### Scenario: Vendor grilling stays Matt
- **WHEN** this change is applied
- **THEN** `.cursor/skills/grilling/SKILL.md` SHALL still contain `❓` and `➡️`
- **AND** MUST NOT gain the operator-ceiling runbook
- **AND** MUST NOT name `AskUserQuestion` or `ask_user_question`

## REMOVED Requirements

### Requirement: Empty frontier of this adapter is six DoD sections and no open operator decision
**Reason**: DoD da grelha encolhe para 3 seções; Vocabulário e Riscos passam a viver no Design.
**Migration**: Use the added requirement `Empty frontier of this adapter is three DoD sections and no open operator decision`. Bodies already grilled with six sections are not rewritten.

### Requirement: Offer-grill trigger stays body without six DoD sections
**Reason**: Disparo e skip passam a quem sofre + entra/não entra (Q2=A), não à ausência das 6 seções.
**Migration**: Use the added requirements `Parent skips a nítido card` and `Offer-grill trigger is missing who-suffers plus entra`.
