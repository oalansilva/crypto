## ADDED Requirements

### Requirement: Grill-card section names the operator language ceiling
`.cursor/skills/covenant-flow/SKILL.md` SHALL include, in the `## Grill-card` section, this exact sentence in addition to the existing host-options relay line:

`Tecto: Qs e options em português de operador em todo card em Em Refinamento; identificador do git é facto no body ou *como* no Design, não option no host; Other vazio, silêncio e «não percebi» / «isto é técnico» reclassificam e nunca aceitam a recomendada.`

The existing offer-grill trigger (body lacks the six DoD sections) and the parent relay of **all** `options[]` (MUST NOT collapse to the recommended) SHALL remain in that section. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `process-fsm.yaml` as a side effect of this sentence, and MUST NOT name the host tool in `.grok/skills/*` stubs.

#### Scenario: Grill-card block names the ceiling besides relay
- **WHEN** a contributor reads the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section SHALL contain the exact ceiling sentence (Other vazio, silêncio, «não percebi»)
- **AND** it SHALL still contain the parent relay of all options (`todas as options` / `não colapsa`)
- **AND** the offer-grill trigger SHALL still be body without the six DoD sections

#### Scenario: No FSM change for the ceiling line
- **WHEN** this change is applied
- **THEN** `process-fsm.yaml` law table is unchanged by the ceiling sentence
- **AND** `AGENTS.md` always-on does not grow with this rule

### Requirement: Operator ceiling ships as product patch pin
This change SHALL ship in product `oalansilva/covenant-flow` as tag **`v1.1.6`** (patch; not a schema major), unless that tag is already taken on origin — in which case Apply SHALL use the next unused patch tag and MUST NOT bump major. `SCHEMA_MAJOR` SHALL remain 1. Apply SHALL commit the canonical `grill-card` ceiling, the exact Grill-card sentence in `covenant-flow`, and goldens in `scripts/process-fsm/test_grill_card.py` in the product first, then `implantar --pin` of that tag on Cripto. Overlay SHALL record `pin` as that tag. Client skins under `.grok/` `.dsh/` `.opencode/` for `grill-card` MUST stay at most 8 non-empty body lines.

#### Scenario: Pin materializes the ceiling on Cripto
- **WHEN** overlay is valid and `implantar --pin` of this card's tag completes on Cripto
- **THEN** `.cursor/skills/grill-card/SKILL.md` contains the operator-language ceiling
- **AND** the `## Grill-card` section of `covenant-flow` contains the exact ceiling sentence
- **AND** overlay contains `pin: v1.1.6` or the next unused patch tag Apply confirmed on origin
- **AND** grill-card stubs under `.grok/` `.dsh/` `.opencode/` remain at most 8 non-empty body lines
