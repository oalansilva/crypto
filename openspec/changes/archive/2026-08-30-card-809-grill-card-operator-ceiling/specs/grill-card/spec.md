## ADDED Requirements

### Requirement: Operator language ceiling on every Em Refinamento card
The adapter `.cursor/skills/grill-card/SKILL.md` SHALL state a language ceiling that applies to **every** card in Project 1 `Status=Em Refinamento` (product stories such as Monitor and process/harness cards alike). Closed questions and their host-tool options MUST be in operator Portuguese: who suffers, what passes/fails, and what is out of this card. A candidate question that is intelligible only with a git identifier (function name, path, yaml flag, flow event, or hash) MUST NOT appear on the host-tool card. That content SHALL be written as a **fact** in the issue body or as *como* (mechanism) under Riscos for Design — never as an option. Entra of the grilled card SHALL describe observable behavior, not the mechanism. The vendored primitive `.cursor/skills/grilling/SKILL.md` MUST NOT be edited for this ceiling. Host-option ritual from the closed-questions requirement (N≥2, every alternative, recommended first) SHALL remain unchanged; only the **content** of questions changes.

#### Scenario: Git identifier is not a host-tool question
- **WHEN** a grill round in Em Refinamento has a candidate closed question that is intelligible only with a function name, path, yaml flag, flow event, or hash
- **THEN** that candidate MUST NOT appear on the host-tool card
- **AND** the fact SHALL go into the issue body or the *como* SHALL go to Riscos for Design

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

### Requirement: Confusion reclassifies and never accepts the recommended option
When the operator input on a closed grill question is **empty Other**, **silence** (no answer), or the phrases «não percebi» / «isto é técnico» (via the host Other field or free text), the adapter SHALL **reclassify** that question (fact into the body or *como* into Design) and MUST NOT record the recommended option as decided. Other closed questions from the same round SHALL remain waiting for an operator answer. Empty Other, silence, and «não percebi» / «isto é técnico» MUST NOT count as acceptance of the recommended option. The host automatic Other line (#755) is not a listed alternative and MUST NOT be treated as a closed-question option whose label is «não percebi».

#### Scenario: nao percebi does not stamp the recommended
- **WHEN** Alan answers a closed grill question with «não percebi» or «isto é técnico» (Other or free text)
- **THEN** the adapter SHALL reclassify that question (fact in the body or *como* in Design)
- **AND** MUST NOT record the recommended option as the decision
- **AND** other questions of the same round SHALL stay unanswered

#### Scenario: Empty Other does not stamp the recommended
- **WHEN** the host Other line is submitted empty on a closed grill question
- **THEN** the adapter MUST NOT record the recommended option as the decision
- **AND** SHALL reclassify or leave that question unanswered

#### Scenario: Silence does not stamp the recommended
- **WHEN** there is no operator answer (silence) on a closed grill question
- **THEN** the adapter MUST NOT record the recommended option as the decision
- **AND** that question SHALL remain open

### Requirement: Golden dumps distinguish ceiling fail from pass
`scripts/process-fsm/test_grill_card.py` SHALL fail a child dump whose closed questions need git identifiers to be intelligible, and SHALL pass a dump whose closed questions are only operator questions (who suffers / what passes or fails / what is out of this card). The golden SHALL use **both** an identifier-list scanner **and** fixed fixture files under `scripts/process-fsm/fixtures/grill_ceiling/`. The scanner MUST NOT flag operator Portuguese: `Não priorizar ainda`, `acabada`, and compact date `20260830` MUST pass `ceiling_violation`. SHA match SHALL be a 40-hex token **or** 7–39 hex with at least one digit and at least one letter `a–f` (MUST NOT be `\b[0-9a-f]{7,40}\b` alone). Event match SHALL be tokens `process_event` or `iniciar_design` only (MUST NOT substring-match the verb `priorizar`). Pytest SHALL include unit asserts that those three operator strings return false and that `process_event priorizar` and mixed-hex `94f8ed41` return true. Fixed fail fixtures SHALL reconstruct the evidence shapes of #795 Q2 (function vs interpolating yaml), #799 Q3 (sum of copy markers), and #801 Q3 (do not measure an internal predicate), plus one product-story equivalent whose options are intelligible only with a Monitor path or component. The operator pass fixture MUST contain `Não priorizar ainda`, `acabada`, and `20260830`. Apply MUST NOT `gh issue edit` those existing issues. Dumps that stamp the recommended option after empty Other, silence, or «não percebi» / «isto é técnico» SHALL fail. A fixture MUST NOT encode «não percebi» as the recommended option **label** (host Other is automatic and outside `options[]`). The golden lives with the adapter (product plus pin).

#### Scenario: Harness evidence dumps fail the golden
- **WHEN** pytest runs the grill ceiling golden
- **THEN** fixtures reconstructing #795 Q2, #799 Q3, and #801 Q3 SHALL fail
- **AND** those GitHub issue bodies SHALL NOT be rewritten by this change

#### Scenario: Product-story equivalent dump fails
- **WHEN** a fixture dump has a closed question whose options are a Monitor path versus a component name
- **THEN** the golden SHALL fail that dump

#### Scenario: Operator-only dump with priorizar acabada and compact date passes
- **WHEN** a fixture dump has only operator questions (who suffers / what passes or fails / what is out of this card) and includes the strings `Não priorizar ainda`, `acabada`, and `20260830`
- **THEN** the golden SHALL pass that dump
- **AND** `ceiling_violation` SHALL be false for each of those three strings

#### Scenario: Wide hash or priorizar substring is a failing matcher
- **WHEN** pytest runs the scanner unit asserts
- **THEN** `ceiling_violation("Não priorizar ainda")`, `ceiling_violation("A história está acabada")`, and `ceiling_violation("evidência 20260830")` SHALL be false
- **AND** `ceiling_violation("process_event priorizar")` and `ceiling_violation("94f8ed41")` SHALL be true

#### Scenario: Stamp after empty Other fails
- **WHEN** a fixture dump records the recommended option as decided after empty Other
- **THEN** the golden SHALL fail that dump

#### Scenario: Stamp after silence fails
- **WHEN** a fixture dump records the recommended option as decided after silence (no answer)
- **THEN** the golden SHALL fail that dump

#### Scenario: Stamp after nao percebi via Other fails
- **WHEN** a fixture dump records the recommended option as decided after Other or free text «não percebi» / «isto é técnico»
- **THEN** the golden SHALL fail that dump
- **AND** the fixture MUST NOT place those phrases as the recommended option label in `options[]`

### Requirement: Empty frontier of this adapter is six DoD sections and no open operator decision
For `grill-card`, an empty frontier SHALL mean the issue body has the six DoD sections **and** no operator decision remains open. The full Matt design tree MAY continue in Design and MUST NOT be required to complete in Em Refinamento. The canonical comment text SHALL remain exactly `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Only the *when* of posting it changes. Idempotence SHALL stay: exact text already present → leave it; wrong canonical grill-card comment → edit or minimize; MUST NOT post a second copy. T1 remains Alan-only. This requirement MUST NOT add a Kanban column or change Status.

#### Scenario: Stop after operator DoD without walking the whole Matt tree
- **WHEN** the issue body has the six DoD sections and no operator decision is open
- **THEN** the child SHALL post or keep exactly one canonical comment `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **AND** MUST NOT keep asking design-tree questions in Em Refinamento
- **AND** MUST NOT change the canonical comment text

#### Scenario: Canonical comment text stays the pinned line
- **WHEN** this change is applied
- **THEN** `.cursor/skills/grill-card/SKILL.md` SHALL still contain the exact substring `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).`
- **AND** MUST NOT introduce a replacement handoff sentence

### Requirement: Offer-grill trigger stays body without six DoD sections
The offer-or-spawn trigger SHALL remain: Project 1 Status of issue N is `Em Refinamento` **and** the issue body lacks the six DoD sections (or Alan asks to grill/afiar). The operator-language ceiling MUST NOT force a re-grill of a card whose body already has the six DoD sections. Cards with a complete DoD MAY still T1 without grill. The ceiling MUST NOT run `grill-card` when Status is Todo or Design. `/opsx:explore`, schema `grill-driven`, `grill-with-docs`, `to-spec`, and a marketplace skill MUST NOT become the Em Refinamento front door; the door remains `grill-card`.

#### Scenario: Complete DoD is not re-grilled by the ceiling
- **WHEN** Status of issue N is `Em Refinamento` and the body already has the six DoD sections
- **THEN** the parent MUST NOT spawn `grill-card` solely because the ceiling exists
- **AND** Alan MAY still T1 without a new grill

#### Scenario: Explore is not the Em Refinamento door
- **WHEN** someone tries `/opsx:explore`, `grill-driven`, or a marketplace skill as the Em Refinamento interview door
- **THEN** the door SHALL remain `grill-card`
- **AND** those entry points MUST NOT replace the adapter

### Requirement: Client skins stay thin MUST Read of the canonical adapter
`.grok/skills/grill-card/SKILL.md`, `.dsh/skills/grill-card/SKILL.md`, and `.opencode/skills/grill-card/SKILL.md` SHALL remain thin stubs that MUST Read `.cursor/skills/grill-card/SKILL.md`. Their bodies SHALL stay at most 8 non-empty lines. Apply MUST NOT copy the operator-ceiling runbook into those stubs. `.grok/skills/grill-card/SKILL.md` and `.grok/skills/grilling/SKILL.md` MUST NOT name `AskUserQuestion` or `ask_user_question`.

#### Scenario: Skins remain MUST Read without the ceiling text
- **WHEN** this change is applied
- **THEN** each of `.grok`, `.dsh`, and `.opencode` `grill-card/SKILL.md` still instructs MUST Read of the canonical skill
- **AND** each stub body has at most 8 non-empty lines
- **AND** the Grok grill-card stub MUST NOT contain `AskUserQuestion` or `ask_user_question`
