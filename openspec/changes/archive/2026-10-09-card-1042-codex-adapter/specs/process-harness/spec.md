## RENAMED Requirements

### Requirement: Process law has one nucleus and four adapters
- FROM: `Process law has one nucleus and four adapters`
- TO: `Process law has one nucleus and five adapters`

## MODIFIED Requirements

### Requirement: Process law has one nucleus and five adapters
The process SHALL have a single nucleus and five client adapters. The nucleus is `.cursor/process-fsm.yaml` (T0–T18, I1–I9, 12 column names, events, `context_file`, `enabled_tools` — **not** `product_globs`/`design_globs`), `scripts/process-fsm/`, the canonical skill files, and the short root `AGENTS.md`. Consumer parameters (`product_globs`, `design_globs`, board ids) live in `.covenant-flow/overlay.yaml` and are NOT a second law table. The Cursor adapter is `.cursor/hooks.json`, `.cursor/hooks/*`, `.cursor/rules/harness.mdc`, and `.cursor/commands/`. The Grok adapter is `.grok/hooks/`, generated Moore paging under `.grok/rules/`, and skill stubs under `.grok/skills/`. The OpenCode adapter is `.opencode/plugin/` (auto-loaded `*.js` / `*.ts`), Moore inject via `experimental.chat.system.transform`, and skill stubs under `.opencode/skills/` only for skills the OpenCode 1.18.18 binary does not discover. The dsh adapter is `.dsh/plugin/` (Cordis `apply(ctx)`), Moore inject via `ctx.systemPrompt.section`, and skill stubs under `.dsh/skills/` only for skills dsh does not discover. The fifth Codex local adapter is project-scoped `.codex/` hooks and thin skill bridges under `.agents/skills/`; CLI and IDE local use the same adapter. A change of column, invariant, or Moore `context_file` text MUST be made once in the yaml (and in a skill only when the change is *how* to work). A change of product glob, design glob, or board ids MUST be made once in the overlay. All adapters SHALL compile law from the yaml and globs/board ids from the overlay. Missing or invalid overlay SHALL fail closed for **product writes**; paging/`sessionStart` remains fail-open (unbound/unread page) and MUST NOT dump the overlay body. Adapters MUST NOT copy T0–T18, I1–I9, or the 12-column runbook. Codex home skills and Hermes skill symlinks MUST NOT be an active contract. The lock machine (`design-planner` lease, packet, `design_artifact_write`, attestation, `opencode.db` as kaizen contract) MUST remain forbidden. `opencode.json` MUST NOT be an active contract of model, MCP, or permission. Neither dsh nor Codex SHALL be a source of law.

#### Scenario: One yaml change reaches five adapters
- **WHEN** a column, invariant, or `context_file` stub changes in `.cursor/process-fsm.yaml`
- **THEN** Cursor, Grok, OpenCode, dsh, and Codex Guard/paging paths compile that law from the yaml
- **AND** no second table exists in any adapter directory

#### Scenario: Dual-write of the law is forbidden
- **WHEN** a reviewer inspects `.cursor/rules/`, `.grok/rules/`, `.opencode/`, `.dsh/`, `.codex/`, and Codex skill bridges
- **THEN** none contains a copied T0–T18 table, invariant list, or 12-column procedure
- **AND** every skill bridge points to the canonical file instead of copying its runbook

#### Scenario: Glob change in overlay reaches five Guards
- **WHEN** a product glob changes in `.covenant-flow/overlay.yaml`
- **THEN** all five Guards classify a corresponding write using the changed overlay glob
- **AND** the glob is not redeclared as yaml law or Codex-local policy

#### Scenario: Fifth harness is not the law
- **WHEN** a reviewer inspects `.codex/` and `scripts/process-fsm/`
- **THEN** `.codex/` contains only event translation/configuration
- **AND** state/event law remains in `.cursor/process-fsm.yaml`

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15/T18, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, OpenCode, dsh, and Codex local ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name all five clients and state they are cooperative. It MUST NOT claim Auto for any client, interpolate `clients.*.auto`, contain `Auto permitido`, or copy the 12-column runbook or `release-guard pre`/`post` snippets. Its header MUST NOT say the stub is “não always-on”. The deny-essay clause for Grok/OpenCode/dsh/Codex MUST NOT turn Cursor into an Auto claim. Naming Codex or dsh MUST NOT depend on a new overlay key.

#### Scenario: Five clients read the same stub
- **WHEN** sessions in the five clients start in the repo
- **THEN** each loads root `AGENTS.md` with the same δ/Status/human-gate guidance
- **AND** Codex CLI and IDE local see the same file
- **AND** the stub names all five clients, Alan-only T1/T7/T15/T18 and consumer `overlay_doc`
- **AND** it contains no Auto claim, `Auto permitido`, FSM table, or release script body

#### Scenario: Overlay auto flags do not drive the stub
- **WHEN** an overlay `clients.*.auto` value changes
- **THEN** `render_agents()` still emits cooperative client wording
- **AND** it does not say `Auto permitido`
