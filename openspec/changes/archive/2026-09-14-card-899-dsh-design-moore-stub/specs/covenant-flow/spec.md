## ADDED Requirements

### Requirement: Design Cliente dsh line spawns the author
The canonical skill `.cursor/skills/covenant-flow/SKILL.md` SHALL contain, in the Design column / children table, one line prefixed `Cliente dsh:` that tells the dsh runtime root to spawn 1 Design-autor and tells the parent not to write OpenSpec on its own turn. That line MUST state that the grill exception does not apply to Design. The Grill-card section MUST keep the existing line `Cliente dsh: dsh não spawna filho grill.` unchanged. The parent exception for writing `## Design Critique` after A/B MUST remain. `AGENTS.md` MUST NOT grow this rule. Client stubs under `.dsh/skills/`, `.grok/skills/`, and `.opencode/skills/` MUST stay at most 8 non-empty body lines and MUST remain MUST Read bridges. `guard.py` `decide()` MUST NOT change for this requirement.

#### Scenario: Design section names the dsh spawn
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` Design column or children table is read
- **THEN** it contains a `Cliente dsh:` line that tells the root to spawn 1 Design-autor
- **AND** that line says the parent does not write OpenSpec on its own turn
- **AND** that line says the grill exception does not apply

#### Scenario: Grill Cliente dsh line stays
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` Grill-card section is read
- **THEN** it contains `Cliente dsh: dsh não spawna filho grill.`
- **AND** `AGENTS.md` does not contain a T0–T17 table
- **AND** dsh/Grok/OpenCode covenant-flow stubs remain at most 8 non-empty body lines

### Requirement: Cursor modes dsh-fora is not T5 deny
The canonical skill `.cursor/skills/covenant-flow/SKILL.md` section `## Modos Cursor (terminal vs Desktop+SSH)` SHALL keep the phrase `Grok / OpenCode / dsh fora` as the #880 InstantiationService / Landlock recorte. The same sentence or the immediately following line MUST state that this phrase is not a deny of T5 / `G_design`. `G_design` SHALL continue to measure OpenSpec files and the clone gate. This requirement MUST NOT drop either Cursor host mode and MUST NOT add a state, event, or `enabled_tools` entry.

#### Scenario: Modos Cursor names T5 is not the host-mode recorte
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` Modos Cursor section is read
- **THEN** it contains `Grok / OpenCode / dsh fora`
- **AND** the same block or the next line states that this is not a deny of T5 / `G_design`

### Requirement: Follow-up pin after v1.1.14 copies Design Moore stub
This change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (live Cripto overlay `pin: v1.1.14`; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.14`. Apply SHALL rebase on the product tip so haystacks from in-flight sibling cards that share nucleus (`process-fsm.yaml` `context_file`, covenant-flow skill, paging goldens) are not reverted. Apply SHALL commit the Design stub reword, the Design `Cliente dsh:` line, the Modos Cursor T5 sentence, and goldens in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a 12-column runbook. `guard.py` `decide()` MUST NOT change. Authenticated dump of dsh web `:3080` SHALL remain the human DoD for one Design-bound turn in which the root spawns the Design-autor (needle `design-autor` / `subagent`) or the child writes under `openspec/changes/`, and MUST NOT be replaced by pytest goldens. A turn that refuses only with `Write produto deny` / «dsh não spawna autor» / «não conta no T5» SHALL fail that dump. A helper that does not open after the root tried without those three refusals is not a failure of this card. Issues #689, #839, #821, and #880 SHALL NOT be reopened as work of this pin.

#### Scenario: Next free patch pin refreshes the Design Moore stub on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `.cursor/process-fsm.yaml` `context_file[Design]` in the consumer contains `OpenSpec/protótipo allow`
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch after `v1.1.14`
- **AND** it is not `v2.0.0`
- **AND** `scripts/process-fsm/guard.py` `decide()` is unchanged by this pin

#### Scenario: Human dump remains mandatory and dsh-only
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows a Design-bound turn where the root spawns the Design-autor or the child writes under `openspec/changes/`
- **AND** a turn that refuses only with the three readings does not satisfy that dump
- **AND** pytest goldens do not replace that dump
- **AND** dumps on Cursor, Grok, or OpenCode are not required
- **AND** a helper that does not open after the root tried without those three refusals is not a failure of this card
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit
