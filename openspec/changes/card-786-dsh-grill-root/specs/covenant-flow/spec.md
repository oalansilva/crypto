## ADDED Requirements

### Requirement: Follow-up pin v1.1.3 copies dsh grill-root Guard and canonical client branch
After #784's always-on pin `v1.1.1`, this change SHALL ship in product `oalansilva/covenant-flow` as tag **`v1.1.3`** (patch; not a schema major). Origin already published `v1.1.2` on the README PT-BR commit; Apply SHALL not move that tag. Apply SHALL commit the updated Guard plugin, `dsh_plugin_lib.js` grill-shaped helper, canonical `grill-card` client-labelled branch, the `Cliente dsh:` line in `covenant-flow` Grill-card, and goldens in the product first, then `implantar --pin v1.1.3` on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin: v1.1.3`. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a dsh-grill line.

#### Scenario: Pin v1.1.3 refreshes the dsh grill deny on Cripto
- **WHEN** overlay is valid and `implantar --pin v1.1.3` completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer denies grill-shaped `subagent` / `subagent_fork`
- **AND** overlay contains `pin: v1.1.3`
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is `v1.1.3`
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin
