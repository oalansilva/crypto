## ADDED Requirements

### Requirement: Follow-up pin v1.1.1 copies the cwd-independent dsh Guard
After #782's four-adapter pin `v1.1.0`, this change SHALL ship in product `oalansilva/covenant-flow` as tag **`v1.1.1`** (patch; not a schema major). Apply SHALL commit the updated Guard plugin, `dsh_plugin_lib.js`, `dsh_boot.sh`, and goldens in the product first, then `implantar --pin v1.1.1` on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin: v1.1.1`. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines.

#### Scenario: Pin v1.1.1 refreshes the dsh plugin on Cripto
- **WHEN** overlay is valid and `implantar --pin v1.1.1` completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer injects the `AGENTS.md` section and registers the process skill provider
- **AND** overlay contains `pin: v1.1.1`
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is `v1.1.1`
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
