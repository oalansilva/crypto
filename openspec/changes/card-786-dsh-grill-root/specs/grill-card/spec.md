## MODIFIED Requirements

### Requirement: grill-card is the Em Refinamento interview front door
The repository SHALL contain `.cursor/skills/grill-card/SKILL.md` as a regular file (not git symlink mode `120000`). The skill SHALL require Project 1 `Status=Em Refinamento` and an explicit GitHub issue id in the spawn prompt (title `#<id>` or equivalent) before editing that issue. It MUST NOT require git branch `card-<id>-*` or a card worktree. Frontmatter SHALL set `disable-model-invocation: false`. This spawn/relay ritual applies to Cursor and Grok. The dsh runtime-root ritual is a separate requirement. On Cursor and Grok, the **parent** session MUST spawn an isolated `grill-card` child (same model, no parent transcript) and MUST only relay rounds: present every closed question with **all** alternatives the child listed, collect Alan's answers, re-spawn or resume the child. The parent MUST NOT collapse a closed question to the recommended option alone. The child SHALL apply the vendored `grilling` primitive and write the DoD sections into the issue body in pt-BR: Problema, História (Como/quero/para), Entra/não entra, Vocabulário (`_Avoid:`), critérios observáveis, Riscos. When the frontier is empty, the child SHALL ensure exactly one canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` exists on the issue: if an existing comment is already that exact text, leave it; if an existing canonical grill-card comment has the wrong text, edit or minimize that comment; MUST NOT post a second copy. When the frontier is not empty, the card MUST remain in Em Refinamento and MUST NOT receive a new copy of that comment. The child MUST NOT call `process_event priorizar`.

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

#### Scenario: Offer grill when body lacks DoD
- **WHEN** the client is Cursor or Grok, Status of issue N is `Em Refinamento`, the body lacks any DoD section, and Alan has not forbidden grilling
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

### Requirement: Closed grill questions list all host-tool options
`.cursor/skills/grill-card/SKILL.md` SHALL state the host-tool contract for both Cursor and Grok. A **closed** frontier question with mutually exclusive real alternatives MUST be presented with every alternative in the host tool `options[]` (Cursor `AskUserQuestion`, Grok `ask_user_question`). N SHALL be the count of those real alternatives and MUST be ≥2. The recommended alternative MUST be the first option; its label MUST include `(Recommended)`. The host automatic Other line MUST NOT count toward N and MUST NOT replace a missing alternative. A closed question MUST NOT be presented with only one option. On Cursor and Grok, the isolated child MUST NOT call the host tool; it SHALL return each closed question with the N options listed (labels A/B/… plus the recommendation, recommended first) so the parent can map them 1:1 into `options[]` in the same order. An **open** (free-text) question MUST be presented as markdown and/or the host Other field; the agent MUST NOT invent fake `options[]` only to make a card appear. When the host tool is unavailable, the fallback SHALL be the Matt markdown format: the **body** of a closed question lists the choices and the `➡️` line is only the recommendation (MUST NOT be only the arrow). `.cursor/skills/grilling/SKILL.md` MUST remain the Matt copy and MUST NOT name the host tools. `.grok/skills/grill-card/SKILL.md` and `.grok/skills/grilling/SKILL.md` MUST NOT name `AskUserQuestion` or `ask_user_question`. The dsh runtime-root `ask_user_question` ritual is a separate requirement.

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
- **WHEN** the isolated grill child on Cursor or Grok returns a closed question
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

## ADDED Requirements

### Requirement: dsh grill runs on the runtime root
When the client is dsh, the **runtime root** SHALL execute skill `grill-card` plus vendored `grilling`, SHALL update issue N via `gh issue edit`, and SHALL call `ask_user_question` for closed frontier questions. The canonical skill MUST instruct that dsh actor to call `ask_user_question` and MUST NOT tell that actor it MUST NOT call the host tool. Closed questions on dsh SHALL use the same N≥2 contract: recommended first with `(Recommended)` in the label; the automatic Other line MUST NOT count toward N. The dsh root MUST NOT call `subagent` or `subagent_fork` whose work is grill — including when `run_in_background` is `false`. There is no child→parent D5 dump on dsh. The canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` MUST NOT be posted as a **new** copy while a closed round is still unanswered; it MAY be posted after answers land or when the frontier is fact-only. On Cursor and Grok, the isolated child MUST NOT call the host tool (unchanged #755).

#### Scenario: dsh root asks before canonical T1
- **WHEN** a dsh web session (preset `standard`, plugin loaded) is asked to refine/grelha issue N in `Em Refinamento` with a frontier that has a decision
- **THEN** the runtime root SHALL call `ask_user_question`
- **AND** that call MUST occur before any new canonical T1 comment
- **AND** the root SHALL edit the issue body toward the DoD
- **AND** the canonical skill MUST NOT tell that dsh actor it MUST NOT call the host tool

#### Scenario: dsh MUST NOT spawn grill-shaped subagent
- **WHEN** a dsh root would otherwise delegate grill-card via `subagent` or `subagent_fork`
- **THEN** the agent MUST NOT make that call
- **AND** `run_in_background: false` does not authorize it
- **AND** there is no D5 dump from a grill child to the dsh parent

#### Scenario: Cursor and Grok parent spawn stays
- **WHEN** a Cursor or Grok parent session grelha issue N in `Em Refinamento`
- **THEN** the parent SHALL still spawn an isolated `grill-card` child
- **AND** that child MUST NOT call `AskUserQuestion` or `ask_user_question`
- **AND** the parent SHALL relay closed questions with all options

### Requirement: Canonical grill-card text is client-labelled
Needles in this requirement SHALL be evaluated after `_plain` (lowercase; collapse whitespace; strip markdown emphasis `*` / `**` / `_word_`; strip backticks; MUST NOT delete `_` inside `ask_user_question`). A no-op `_plain = lower+whitespace` MUST fail the first fixture. Pytest SHALL include these exact fixtures:

```
assert "não chama a ferramenta do host" in _plain("**não** chama a ferramenta do host")
assert _plain("ask_user_question") == "ask_user_question"
assert "o pai spawna" in _plain("O **pai** spawna")
assert "root chama ask_user_question" not in _plain("O runtime root nunca chama ask_user_question.")
assert "root chama ask_user_question" not in _plain("O runtime root não chama. chama ask_user_question.")
assert "root chama ask_user_question" in _plain("O runtime root chama `ask_user_question`.")
```

`.cursor/skills/grill-card/SKILL.md` SHALL place every sentence that (a) says the grill actor/child MUST NOT call the host tool (including `**não** chama`), (b) says the parent spawns (`O **pai** spawna`) or the parent calls the host tool (live Perguntas: `Quem chama \`AskUserQuestion\` … é o **pai**`), or (c) describes dump D5 child→parent, **only** under the heading `## Cliente: Cursor e Grok`. `## Precondição` MAY keep Status=`Em Refinamento` and issue id N and, after `_plain`, MUST NOT contain `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, or `não chama`. The live H2 `## Perguntas da rodada (host)` (with or without `(host)`) MUST NOT remain a shared top-level section that assigns host-calling to the parent: Apply SHALL move that body under Cursor e Grok (nested `###` allowed) or replace it with two labelled branches. Heading `## Cliente: dsh` SHALL, after `_plain`, contain the contiguous substring `root chama ask_user_question`, and MUST NOT contain `não chama ask_user_question` or `não chama a ferramenta do host`. The dsh section MUST say the dsh rule does **not** apply to Cursor, Grok, or OpenCode. `.cursor/skills/covenant-flow/SKILL.md` Grill-card section SHALL include one line prefixed `Cliente dsh:` that dsh does not spawn a grill child. Frontmatter MAY still mention spawn prompt. `.dsh/skills/grill-card/SKILL.md` SHALL remain a thin MUST Read stub (body at most 8 non-empty lines). `scripts/process-fsm/dsh_stubs.py` MUST NOT gain a long-stub exception. Root `AGENTS.md` MUST NOT gain a dsh-grill always-on line.

#### Scenario: Canonical skill has two labelled sections
- **WHEN** a contributor reads `.cursor/skills/grill-card/SKILL.md` after `_plain`
- **THEN** heading `## Cliente: Cursor e Grok` exists and that section contains `não chama a ferramenta do host`, `o pai spawna`, `dump d5`, and `quem chama`
- **AND** heading `## Cliente: dsh` exists and after `_plain` that section contains the contiguous substring `root chama ask_user_question` and MUST NOT contain `não chama ask_user_question` or `não chama a ferramenta do host`
- **AND** `_plain("O runtime root nunca chama ask_user_question.")` and `_plain("O runtime root não chama. chama ask_user_question.")` SHALL NOT contain `root chama ask_user_question`
- **AND** `_plain("O runtime root chama \`ask_user_question\`.")` SHALL contain `root chama ask_user_question`
- **AND** `_plain("o runtime root não chama ask_user_question")` SHALL fail because it contains `não chama ask_user_question`
- **AND** for each of `não chama a ferramenta do host`, `o pai spawna`, `dump d5`, and `quem chama`, `_plain(file).count(phrase)` equals `_plain(cursor section).count(phrase)` and `_plain(cursor section).count(phrase) >= 1`

#### Scenario: Shared Precondicao has no host-prohibition
- **WHEN** heading `## Precondição` is present in `.cursor/skills/grill-card/SKILL.md`
- **THEN** after `_plain` that section MUST NOT contain `filho`, `spawna`, `relaying`, `dump d5`, `ask_user_question`, `askuserquestion`, or `não chama`

#### Scenario: Perguntas H2 is not a shared top-level host assignment
- **WHEN** Apply has finished
- **THEN** no H2 heading matching `Perguntas da rodada` (with or without `(host)`) exists outside `## Cliente: Cursor e Grok` and `## Cliente: dsh`
- **AND** the live title `## Perguntas da rodada (host)` left as a sibling of `## Precondição` is a failing fixture

#### Scenario: covenant-flow Grill-card names dsh without a global never-spawn
- **WHEN** a contributor reads the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section still says the parent spawns the grill child and relays all options
- **AND** it contains a `Cliente dsh:` line that dsh does not spawn a grill child

#### Scenario: AGENTS.md and dsh stubs stay thin
- **WHEN** this change is applied
- **THEN** root `AGENTS.md` has no dsh-grill always-on line and remains at most 40 non-empty lines
- **AND** `.dsh/skills/grill-card/SKILL.md` still instructs MUST Read of the canonical skill
- **AND** `dsh_stubs.py` is not edited
