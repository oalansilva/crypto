## ADDED Requirements

### Requirement: Explicit-release pedido unbound is not T16 deny
The canonical skill `.cursor/skills/covenant-flow/SKILL.md` Release section SHALL state that `bound_card=⊥` and `enabled_events: (unbound)` are paging display, not T16 deny. An explicit closeout pedido (`suba a release` / `fechar release` / `subir lote`) on an unbound session whose `q_git` is `develop` or `release-*` MUST load overlay on-demand (`overlay_doc` / `covenant-flow-environments`) and follow the T16 playbook. Product Write on `develop` / unbound MUST remain deny. The skill MUST NOT dump the 12-column runbook. `AGENTS.md` MUST NOT grow this rule. Client stubs under `.dsh/skills/`, `.grok/skills/`, and `.opencode/skills/` MUST stay at most 8 non-empty body lines and MUST remain MUST Read bridges. `process-fsm.yaml`, `process_event.py`, `t16.py`, and `guard.py` `decide()` MUST NOT change for this requirement.

#### Scenario: Release section names the unbound exception
- **WHEN** `.cursor/skills/covenant-flow/SKILL.md` Release section is read
- **THEN** it states that paging unbound is not T16 deny for an explicit closeout pedido
- **AND** it tells the agent to load overlay on-demand
- **AND** `AGENTS.md` does not contain a T0–T17 table
- **AND** dsh/Grok/OpenCode covenant-flow stubs remain at most 8 non-empty body lines

#### Scenario: Delta and T16 measurers stay untouched
- **WHEN** a reviewer inspects this change's diff
- **THEN** `.cursor/process-fsm.yaml` is unchanged
- **AND** `scripts/process-fsm/process_event.py` and `scripts/process-fsm/t16.py` are unchanged
- **AND** `scripts/process-fsm/guard.py` `decide()` has no new needles for this card

### Requirement: Follow-up pin after v1.1.13 copies unbound T16 Moore stub
This change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (live Cripto overlay `pin: v1.1.13`; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.13`. Apply SHALL rebase on the product tip so haystacks from in-flight sibling cards that share nucleus (`paging.py`, session-start fallback, covenant-flow skill) are not reverted. Apply SHALL commit the `UNBOUND_PAGE` reword, the Cursor `sessionStart` fallback aligned to that constant, the Release-section line, and paging goldens in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a 12-column runbook. `deepseek-ai/deepseek-harness` MUST NOT be vendored. `process-fsm.yaml` MUST NOT change. Authenticated dump of dsh web `:3080` SHALL remain the human DoD for one unbound explicit closeout (`suba a release` or `fechar release`) and MUST NOT be replaced by pytest goldens. Issues #613, #652, #812, #782, #784, #786, and #817 SHALL NOT be reopened as work of this pin. This card MUST NOT execute a PROD lote.

#### Scenario: Next free patch pin refreshes the unbound Moore stub on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `scripts/process-fsm/paging.py` in the consumer contains the unbound stub that names the explicit-closeout exception
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch after `v1.1.13`
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin

#### Scenario: Human dump remains mandatory and dsh-only
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows an unbound `suba a release` or `fechar release` turn with at least one T16 playbook tool call
- **AND** skill-plus-read of the runbook alone does not satisfy that dump
- **AND** pytest goldens do not replace that dump
- **AND** dumps on Cursor, Grok, or OpenCode are not required
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit
- **AND** this card does not execute a PROD lote
