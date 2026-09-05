## ADDED Requirements

### Requirement: Follow-up pin v1.1.7 copies dsh reasoning-effort Guard
After the operator-ceiling pin `v1.1.6`, this change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (`v1.1.7` when that tag is free; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.6`. Sibling issue #818 (`card-818-dsh-grill-spawn-cite`, Status=Design) edits the same `dsh_plugin_lib.js` and Guard plugin and also hoped for `v1.1.7`; Apply SHALL rebase on the product tip so that card's haystacks are not reverted, and `--pin` of the newer tag SHALL contain both deltas when both have landed. This sibling pin collision is a named residual, not a reason to skip the reasoning-effort sanitize. Apply SHALL commit the Guard plugin `agent/request` / `agent/request-error` listeners, `sanitizeReasoningEffort` / `isReasoningEffortRejection` in `dsh_plugin_lib.js`, the spawn gate `dsh_reasoning_effort_spawn` keyed by `parentSession` (child detected from `agent.session.header`, never from LLM `payload.provider`), the dsh-labelled covenant-flow line (after this-class 400 on a child, MUST NOT spawn the same preset; residual `#518` on the root), and goldens in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a reasoning-effort line. `deepseek-ai/deepseek-harness` MUST NOT be vendored. `process-fsm.yaml` MUST NOT change. Authenticated dump of dsh web `:3080` (Q3=A) SHALL remain the human DoD for one isolated Apply or reviewer spawn and MUST NOT be replaced by pytest goldens.

#### Scenario: Next free patch pin refreshes the dsh reasoning-effort sanitize on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer sanitizes rejected reasoning effort on `agent/request`
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch (`v1.1.7` when free)
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin

#### Scenario: Pin does not revert sibling #818
- **WHEN** #818 has already landed on the product tip before this card tags
- **THEN** Apply rebases so `dsh_plugin_lib.js` and the Guard plugin keep both haystacks
- **AND** `--pin` of the newer tag contains both deltas

#### Scenario: Human dump remains mandatory
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows one isolated Apply or reviewer spawn entering the turn, running at least one tool, and leaving a closing message with zero this-class rejections on that spawn
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit
