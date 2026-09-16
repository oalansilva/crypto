## ADDED Requirements

### Requirement: Grill-card section names nítido skip and three-section DoD
`.cursor/skills/covenant-flow/SKILL.md` section `## Grill-card` SHALL contain the exact substring `card nítido; sem grill` and SHALL state that an empty grill frontier is **3 seções** (Problema, História, Entra/não entra) plus no open operator decision. The offer-or-spawn trigger SHALL be Em Refinamento and a body that does not already state who suffers and what entra/não entra, or an explicit ask to grelhar/afiar. The section MUST NOT contain the substring `6 seções do DoD`. The existing operator-language ceiling sentence and the parent relay of **all** `options[]` (MUST NOT collapse to the recommended) SHALL remain. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `process-fsm.yaml`, and MUST NOT copy these sentences into `.grok/` `.dsh/` `.opencode/` stubs.

#### Scenario: Grill-card block names skip and three sections
- **WHEN** a contributor reads the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section SHALL contain `card nítido; sem grill` and `3 seções`
- **AND** it SHALL still contain the exact ceiling sentence (Other vazio, silêncio, «não percebi»)
- **AND** it SHALL still contain the parent relay of all options (`todas as options` / `não colapsa`)
- **AND** it MUST NOT contain `6 seções do DoD`

#### Scenario: No FSM change for the lean grill
- **WHEN** this change is applied
- **THEN** `process-fsm.yaml` law table is unchanged by the lean-grill sentences
- **AND** `AGENTS.md` always-on does not grow with this rule

### Requirement: Design briefing is three sections on the issue and the package is the Gist superset
`.cursor/skills/covenant-flow/SKILL.md` (Card primeiro / OpenSpec) and `.cursor/skills/openspec-new-change/SKILL.md` plus `.cursor/skills/openspec-ff-change/SKILL.md` SHALL treat a bound Design issue as briefed when the body has Problema, História, and Entra/não entra. They MUST NOT require Vocabulário, critérios as a top-level section, or Riscos on the issue. `proposal.md` and the published Gist SHALL be a **superset** of the issue: history copied from the grilled body (Problema, História, Entra / não entra, Q1–Q3) plus the *como*. Vocabulário and Riscos SHALL be born in `design.md`. The package MUST NOT invent a new story and MUST NOT re-interview. If a required briefing section is missing on the issue, the agent SHALL comment the gaps on the issue and remain in Design; it MUST NOT `/opsx:ff` inventing story text. `G_design` on T5 SHALL continue to require OpenSpec files plus the clone gate plus a Gist comment on the card. Schema `grill-driven` MUST NOT be introduced. This requirement MUST NOT dual-write law into `.dsh/` `.grok/` `.opencode/`.

#### Scenario: New-change briefing is three sections
- **WHEN** a contributor reads `.cursor/skills/openspec-new-change/SKILL.md` and `.cursor/skills/openspec-ff-change/SKILL.md`
- **THEN** the bound-issue briefing list is Problema, História, Entra/não entra
- **AND** it MUST NOT list Vocabulário or Riscos as required grill DoD sections for that briefing

#### Scenario: Proposal copies the grilled story
- **WHEN** `/opsx:ff` writes `proposal.md` for a grilled Design card
- **THEN** `proposal.md` SHALL contain `## Problema`, `## História`, and `## Entra` copied from the issue (or an observable equivalent)
- **AND** MUST NOT invent a new story or re-interview
- **AND** a `proposal.md` without those headings SHALL fail the golden
- **AND** a fixture that copies those headings from the issue SHALL pass

#### Scenario: Card primeiro Gist is superset not only the how
- **WHEN** a contributor reads the Card primeiro section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section SHALL state the Gist is a **superset** of the issue (copied history plus *como*)
- **AND** MUST NOT state that the Gist is only the *como*

#### Scenario: Missing briefing section stays in Design
- **WHEN** the bound Design issue lacks one of Problema, História, Entra/não entra
- **THEN** the agent SHALL comment the gaps
- **AND** MUST NOT fast-forward inventing story text
- **AND** MUST NOT call `process_event submeter_design`

### Requirement: Lean grill ships as product patch pin
This change SHALL ship in product `oalansilva/covenant-flow` as tag **`v1.1.16`** (patch; not a schema major), unless that tag is already taken on origin — in which case Apply SHALL use the next unused patch tag and MUST NOT bump major. `SCHEMA_MAJOR` SHALL remain 1. Apply SHALL commit the canonical `grill-card` lean-grill adapter, the runbook sentences, `openspec-new-change` / `openspec-ff-change` briefing, kaizen release needles, and goldens in `scripts/process-fsm/test_grill_card.py` in the product first, then `implantar --pin` of that tag on Cripto. Overlay SHALL record `pin` as that tag. Client skins under `.grok/` `.dsh/` `.opencode/` for `grill-card` and `covenant-flow` MUST stay at most 8 non-empty body lines.

#### Scenario: Pin materializes the lean grill on Cripto
- **WHEN** overlay is valid and `implantar --pin` of this card's tag completes on Cripto
- **THEN** `.cursor/skills/grill-card/SKILL.md` contains the three-section DoD and the one-pass ceiling
- **AND** the `## Grill-card` section of `covenant-flow` contains `card nítido; sem grill`
- **AND** overlay contains `pin: v1.1.16` or the next unused patch tag Apply confirmed on origin
- **AND** grill-card stubs under `.grok/` `.dsh/` `.opencode/` remain at most 8 non-empty body lines

## MODIFIED Requirements

### Requirement: Grill-card section names the operator language ceiling
`.cursor/skills/covenant-flow/SKILL.md` SHALL include, in the `## Grill-card` section, this exact sentence in addition to the existing host-options relay line:

`Tecto: Qs e options em português de operador em todo card em Em Refinamento; identificador do git é facto no body ou *como* no Design, não option no host; Other vazio, silêncio e «não percebi» / «isto é técnico» reclassificam e nunca aceitam a recomendada.`

The offer-grill trigger SHALL be a body that does not already state who suffers and what entra/não entra (nítido skip is a sibling requirement) or an explicit ask to grelhar/afiar. The parent relay of **all** `options[]` (MUST NOT collapse to the recommended) SHALL remain in that section. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `process-fsm.yaml` as a side effect of this sentence, and MUST NOT name the host tool in `.grok/skills/*` stubs.

#### Scenario: Grill-card block names the ceiling besides relay
- **WHEN** a contributor reads the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section SHALL contain the exact ceiling sentence (Other vazio, silêncio, «não percebi»)
- **AND** it SHALL still contain the parent relay of all options (`todas as options` / `não colapsa`)
- **AND** the offer-grill trigger SHALL NOT require the six DoD sections

#### Scenario: No FSM change for the ceiling line
- **WHEN** this change is applied
- **THEN** `process-fsm.yaml` law table is unchanged by the ceiling sentence
- **AND** `AGENTS.md` always-on does not grow with this rule
