## RENAMED Requirements

### Requirement: Four adapters ship in every consumer
- FROM: `Four adapters ship in every consumer`
- TO: `Five adapters ship in every consumer`

## MODIFIED Requirements

### Requirement: Product repository is oalansilva/covenant-flow
The portable process product SHALL live in the private GitHub repository `oalansilva/covenant-flow` (display name Covenant Flow). The nucleus SHALL be `process-fsm.yaml`, `scripts/process-fsm/` (`guard`, `resolve`, `process_event`, `paging`, goldens), and the canonical skill files. Product and skill names MUST NOT contain `alan`. The product MUST NOT ship Funil Cripto copy, `PRODUCT.md` / `DESIGN.md` / token-sheet content, or PostgreSQL as an always-on of the package. The product SHALL ship five client adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`, `.codex/` plus Codex skill bridges under `.agents/skills/`). It MUST NOT vendor `deepseek-ai/deepseek-harness`.

#### Scenario: Fresh clone of the product repo
- **WHEN** a machine clones a product tag that includes the fifth adapter
- **THEN** the tree contains the nucleus, canonical skills, all five adapters, `install.sh`, and the overlay template
- **AND** no skill directory or product name contains `alan`
- **AND** no Funil Cripto or token-sheet brand content is in the package
- **AND** the DeepSeek Harness monorepo is not vendored

#### Scenario: Host trial folder is not a product artifact
- **WHEN** a reviewer inspects the product repository and this OpenSpec change
- **THEN** `/home/ubuntu/covenant-flow-trial` is not shipped, committed, or cited as a canonical artifact
- **AND** host backup SHA `94f8ed41` is not a product restore requirement

### Requirement: implantar copies nucleus adapters agents skills helpers and the consumer commits them
Skill `implantar` (Portuguese) plus `install.sh --pin` SHALL copy into the consumer the nucleus (`process-fsm.yaml`, `scripts/process-fsm/`), five adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`, `.codex/`), `.agents/skills/` (Impeccable, design-critic, playwright-cli and Codex bridges), helpers (`publish-openspec-card-artifacts.sh`, generic `release-guard`, dsh boot helper), and the template `AGENTS.md`. `install.sh --pin` SHALL copy `.dsh/` and `.codex/` **always**, independent of optional `clients.*` overlay entries. Existing unrelated Codex hooks and Impeccable provider files MUST be preserved or an unsafe conflict MUST fail visibly. For `.cursor/model-map.yaml`, the pin SHALL read the **target consumer file** at installation time, preserve top-level `juizo.label/slug`, `execucao.label/slug`, and every `forbid` entry, and add only the Codex subblocks; a local conflict MUST cause visible refusal or an explicit inspected merge, never silent overwrite from the product or Design worktree. The consumer git SHALL commit those trees (not gitignore, not submodule pointers). On Cripto, which already has `scripts/process-fsm/`, pin SHALL update them to the overlay-reading Guard. The overlay SHALL record `pin` as a semver tag `vMAJOR.MINOR.PATCH`. Updating SHALL mean re-implantar plus commit of the diff. Bump MUST preserve project overlay keys (board, environments, globs, `overlay_doc`) and refresh nucleus/skins/helpers + `pin`. v1 MUST NOT use submodule, native marketplace, or template-clone as the primary channel.

#### Scenario: Pin materializes five adapters in consumer git
- **WHEN** overlay is valid and `implantar --pin <tag>` completes
- **THEN** `.cursor/`, `.grok/`, `.opencode/`, `.dsh/`, `.codex/`, and required `.agents/skills/` bridges/providers exist in the consumer
- **AND** the shared `scripts/process-fsm/`, helpers, and generated `AGENTS.md` exist
- **AND** those trees are committed in the consumer git and overlay `pin` equals `<tag>`
- **AND** bridge stubs remain thin and no adapter copies the FSM table

#### Scenario: Bump is re-implant plus commit
- **WHEN** the consumer moves from one valid pin tag to the next
- **THEN** nucleus, skins, bridges, and helpers are copied again and their diff is committed
- **AND** board, environments, globs, `overlay_doc`, and unrelated Codex hook entries are not reset

#### Scenario: Unsafe hook conflict stops installation
- **WHEN** a consumer has a conflicting or malformed `.codex/hooks.json` that cannot be merged without loss
- **THEN** `implantar --pin` fails visibly
- **AND** it does not report a successful half-applied pin

#### Scenario: Target model map survives the pin
- **WHEN** the consumer's Cursor top-level model values or `forbid` entries differ from the product source or Design worktree at pin time
- **THEN** the installed map retains the consumer's current `juizo.label/slug`, `execucao.label/slug`, and all `forbid` entries
- **AND** only the Codex subblocks are added
- **AND** an incompatible conflict produces visible refusal or an explicit inspected merge, not a successful silent overwrite

#### Scenario: Submodule is not the v1 channel
- **WHEN** a consumer is implanted on v1
- **THEN** no adapter is a git submodule pointer as the primary install
- **AND** skins are not gitignored

### Requirement: Five adapters ship in every consumer
Every implanted consumer SHALL receive the Cursor adapter (`.cursor/hooks.json` `sessionStart`, `preToolUse` failClosed, `beforeShellExecution`, `afterFileEdit`/`stop` Impeccable, `harness.mdc`, `/opsx-*` commands), the Grok adapter (`.grok/hooks/` `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`), the OpenCode 1.18.18 adapter (`.opencode/plugin/` `tool.execute.before` throw on deny, `experimental.chat.system.transform`, `tool.execute.after` + `session.idle` fail-open), the dsh adapter (`.dsh/plugin/` `tools/pre-execute` `{ kind: 'deny' }` fail-closed, `systemPrompt.section` Moore, `tools/post-execute` + `agent/turn-stopping` fail-open), and the Codex local adapter (`.codex/` hooks `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, plus `.agents/skills/` bridges). Each adapter SHALL translate only to the shared Guard, paging, process events, and Impeccable detector. Dual-write of T0–T18 or I1–I9 into any adapter remains forbidden. The lock machine and `opencode.json` as a model/MCP/permission contract remain forbidden. Codex hook coverage is a cooperative guardrail until local CLI and IDE deny essays demonstrate the covered routes; no adapter or `AGENTS.md` may claim Codex Auto.

#### Scenario: Integration branch denies on five clients
- **WHEN** Cripto is pinned and a covered product Write is attempted with `q_git=develop`
- **THEN** Cursor, Grok Build, OpenCode 1.18.18, dsh, and trusted Codex local hooks deny it
- **AND** no adapter contains a copied FSM table

#### Scenario: Current Cripto skins stay until pin
- **WHEN** Apply has not committed the new pin in consumer git
- **THEN** existing Cripto `.cursor/`, `.grok/`, `.opencode/`, and `.dsh/` skins remain in place
- **AND** the fifth adapter appears through the pin after `Pronto para Dev`, not through an early product edit

#### Scenario: Codex coverage remains cooperative
- **WHEN** the Codex local hook is not trusted or a tool path bypasses `PreToolUse`
- **THEN** the essay records that gap and the product does not claim Auto for Codex
