## ADDED Requirements

### Requirement: Follow-up pin after v1.1.9 copies dsh isolate reload helper
After live overlay pin `v1.1.9` (#817/#839 Guard blobs in git; isolate on `:3080` still stale until bounce), this change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (expected `v1.1.10` when that tag is free; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.9`. Apply SHALL rebase on the product tip so haystacks from #817 and #839 already in `v1.1.9` are not reverted. Apply SHALL commit `scripts/process-fsm/dsh_isolate_reload.sh`, the `dsh_boot.sh` call to replace the live isolate and write the sidecar (`DSH_ISOLATE_SIDECAR` or live default `/tmp/covenant-flow-dsh-isolate.json`), and goldens R1–R9 including R5b (plus A7–A9 regression with ephemeral listen and sidecar) in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. Consumer `overlay_doc` (`docs/crypto-overlay.md`) MUST gain 1–3 sentences: after pin/merge of `.dsh/plugin` or `dsh_plugin_lib`, bounce via `dsh_boot.sh`; 3080 ≠ systemd; 3080 ≠ `./restart` of product. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain an isolate-reload line. `@deepseek-ai/dsh*` MUST NOT be vendored. `process-fsm.yaml` MUST NOT change. Issue #846 (`rsync --delete`) SHALL remain its own issue. Issues #817, #839, #837, and #793 SHALL NOT be reopened as work of this pin. Authenticated dump of dsh web `:3080` plus `--check` PASS SHALL remain the human DoD and MUST NOT be replaced by pytest goldens.

#### Scenario: Next free patch pin refreshes the dsh isolate bounce on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `scripts/process-fsm/dsh_boot.sh` in the consumer invokes the isolate-reload sibling before `dsh web --patch`
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch after `v1.1.9` (`v1.1.10` when free)
- **AND** it is not `v2.0.0`
- **AND** `@deepseek-ai/dsh*` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin
- **AND** overlay `pin: v1.1.9` is not moved by Design; Apply writes the confirmed tag

#### Scenario: Pin does not reopen related cards as work
- **WHEN** this card's product commit lands on the covenant-flow tip
- **THEN** Apply has rebased so `dsh_plugin_lib.js` and the Guard plugin keep the #817/#839 sanitizer and Diagnostic haystacks
- **AND** this change's tasks do not include reopening #817, #839, #837, #793, or #846

#### Scenario: Overlay doc records bounce after pin
- **WHEN** this change is applied on Cripto
- **THEN** `docs/crypto-overlay.md` dsh section contains 1–3 sentences that bounce via `dsh_boot.sh` follows pin/merge of `.dsh/plugin` or `dsh_plugin_lib`, that 3080 is not systemd, and that 3080 is not `./restart` of product
- **AND** `AGENTS.md` does not gain an isolate-reload line

#### Scenario: Human dump and isolate check remain mandatory
- **WHEN** this card claims human acceptance
- **THEN** `dsh_isolate_reload.sh --check` PASSes against the live isolate
- **AND** an authenticated dump of `http://127.0.0.1:3080` shows the first-root-turn and isolated-spawn criteria
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit of this card
