## ADDED Requirements

### Requirement: Follow-up pin after v1.1.9 copies dsh idle-closeout Guard
After live overlay pin `v1.1.9`, this change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (expected `v1.1.10` when that tag is free; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.9`. Apply SHALL rebase on the product tip so haystacks already in `v1.1.9` are not reverted. Apply SHALL commit the Guard wait-in-turn (`job_output` rewrite/loop, `agent/turn-stopping` steer, `dsh_dead_turn` one-retry), `dsh_plugin_lib.js` helpers, `.dsh/cordis.patch.yml` `tool-jobs` `maxWaitTimeoutMs` 2400000 (without raising `maxConsecutiveWakes`), Moore `context_file[QA]` dsh wording, skill QA dsh wait-in-turn line, and goldens W1–W8 (`import { apply }` from the plugin) in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain an idle-closeout line. `@deepseek-ai/dsh*` MUST NOT be vendored. Authenticated dump of dsh web `:3080` SHALL remain the human DoD for a QA closeout with several consecutive waits and no `continue` prompt, and MUST NOT be replaced by pytest goldens.

#### Scenario: Next free patch pin refreshes dsh idle-closeout on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer wraps `job_output` wait and steers `turn-stopping` when agent work is pending
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch after `v1.1.9` (`v1.1.10` when free)
- **AND** it is not `v2.0.0`
- **AND** `@deepseek-ai/dsh*` is still not vendored
- **AND** overlay `pin: v1.1.9` is not moved by Design; Apply writes the confirmed tag

#### Scenario: Human dump remains mandatory
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows a QA closeout with several consecutive waits and no prompt `continue`
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit

## MODIFIED Requirements

### Requirement: QA closeout runbook is client-labeled
`.cursor/skills/covenant-flow/SKILL.md` SHALL document QA closeout without adding a FSM state or event. Under the Cursor/Grok path it SHALL say: one isolated QA child reads checks and MUST NOT call `process_event`; the parent calls `aceitar_sha` only after a PR `q_git`→develop exists, then calls `integrar_develop` in the same turn as a green child, waits and retries on `qa-gate pending`, and treats `no_pr` / `sync: dirty` as visible causes. Under a dsh-labeled path it SHALL say: the runtime root MUST NOT spawn a QA child; the same turn MUST open the PR before T11, wait for `qa-gate` **in the turn** (`job_output wait`, without `continue`), and call T14 (Moore/plugin, not skill text alone). Stubs under `.dsh/skills/` and `.grok/skills/` MUST remain thin and MUST NOT copy the 12-column runbook. `AGENTS.md` MUST NOT grow for this rule.

#### Scenario: Cursor path keeps the QA child off process_event
- **WHEN** `covenant-flow` is read for the Cursor client
- **THEN** it says the QA child reads checks and MUST NOT call `process_event`
- **AND** it says the parent calls T14 in the same turn as a green child

#### Scenario: dsh path does not spawn a QA child
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says the root MUST NOT spawn a QA child
- **AND** it says the same turn opens the PR before T11, waits for `qa-gate`, and calls T14

#### Scenario: dsh path waits in the turn without continue
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says to wait for `qa-gate` in the turn
- **AND** it says not to use `continue` for that wait
