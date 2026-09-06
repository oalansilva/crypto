## ADDED Requirements

### Requirement: Follow-up pin after v1.1.8 copies dsh child-spawn Guard
After live overlay pin `v1.1.8` (#817 sanitizer/retry on the host plugin ctx), this change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (expected `v1.1.9` when that tag is free; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.8`. Apply SHALL rebase on the product tip so haystacks from #817 and #818 already in `v1.1.8` are not reverted. Apply SHALL commit the Guard `agent/created` attach onto each `agent.ctx` (`attachAgentEffortGuards` with `{ prepend: true }`, MUST NOT throw), `session/event` `{ global: true }` capture of child `turn/end`, settlement delivery on the parent via `followup`/`steer` (not `inject` as the accept vehicle) with `stopReason` + `Diagnostic` + class `dsh_reasoning_effort_none`, foreground `tools/execute` inspect of `next()` `isError` (not throw-only; `send_message` on the settlement path), helpers in `dsh_plugin_lib.js`, and goldens F1–F8 (isolated child bus + F7 settlement; not only #817 E3–E8 or F5 throw) in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a spawn-isolado line. `@deepseek-ai/dsh*` MUST NOT be vendored. `process-fsm.yaml` MUST NOT change. Authenticated dump of dsh web `:3080` SHALL remain the human DoD for one isolated spawn (Design-autor or `PROBE_OK`) and MUST NOT be replaced by pytest goldens. Issues #817 and #818 SHALL NOT be reopened as work of this pin.

#### Scenario: Next free patch pin refreshes the dsh child agentCtx sanitize on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer attaches effort guards on `agent/created` onto `agent.ctx`
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch after `v1.1.8` (`v1.1.9` when free)
- **AND** it is not `v2.0.0`
- **AND** `@deepseek-ai/dsh*` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin
- **AND** overlay `pin: v1.1.8` is not moved by Design; Apply writes the confirmed tag

#### Scenario: Pin does not reopen #817 or #818 as work
- **WHEN** this card's product commit lands on the covenant-flow tip
- **THEN** Apply has rebased so `dsh_plugin_lib.js` and the Guard plugin keep the #817 sanitizer helpers and the #818 grill citation haystacks
- **AND** this change's tasks do not include reopening those issues

#### Scenario: Human dump remains mandatory
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows one isolated Design-autor or `PROBE_OK` spawn entering `turn/start`, running at least one tool or returning `PROBE_OK`, and closing with zero this-class 400s on that spawn
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit
