## RENAMED Requirements

### Requirement: Three adapters ship in every consumer
- FROM: `Three adapters ship in every consumer`
- TO: `Four adapters ship in every consumer`

## MODIFIED Requirements

### Requirement: Product repository is oalansilva/covenant-flow
The portable process product SHALL live in the private GitHub repository `oalansilva/covenant-flow` (display name Covenant Flow). The nucleus SHALL be `process-fsm.yaml`, `scripts/process-fsm/` (`guard`, `resolve`, `process_event`, `paging`, goldens), and the canonical skill files. Product and skill names MUST NOT contain `alan`. The product MUST NOT ship Funil Cripto copy, `PRODUCT.md` / `DESIGN.md` / token-sheet content, or PostgreSQL as an always-on of the package. The product SHALL ship four client adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`). The product MUST NOT vendor `deepseek-ai/deepseek-harness`.

#### Scenario: Fresh clone of the product repo
- **WHEN** a machine clones `oalansilva/covenant-flow` at tag `v1.1.0`
- **THEN** the tree contains the nucleus, the 20 canonical skills, four client adapters including `.dsh/`, `install.sh`, and the overlay template
- **AND** no skill directory or product name contains `alan`
- **AND** no Funil Cripto or token-sheet brand content is in the package
- **AND** the DeepSeek Harness monorepo is not vendored

#### Scenario: Host trial folder is not a product artifact
- **WHEN** a reviewer inspects the product repository and this OpenSpec change
- **THEN** `/home/ubuntu/covenant-flow-trial` is not shipped, committed, or cited as a canonical artifact
- **AND** host backup SHA `94f8ed41` is not a product restore requirement

### Requirement: implantar copies nucleus adapters agents skills helpers and the consumer commits them
Skill `implantar` (Portuguese) plus `install.sh --pin` SHALL copy into the consumer: the nucleus (`process-fsm.yaml` and `scripts/process-fsm/`), the four adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`), `.agents/skills/` (`impeccable`, `design-critic`, `playwright-cli`), helpers (`publish-openspec-card-artifacts.sh`, generic `release-guard`, dsh boot helper), and the template `AGENTS.md`. `install.sh --pin` SHALL copy `.dsh/` **always**, including when overlay omits `clients.dsh`. The consumer git SHALL commit those trees (not gitignore, not submodule pointers). On Cripto, which already has `scripts/process-fsm/`, pin SHALL update them to the overlay-reading Guard. The overlay SHALL record `pin` as a semver tag `vMAJOR.MINOR.PATCH`. This change's product tag SHALL be **`v1.1.0`**. Updating SHALL mean re-implantar plus commit of the diff. Bump MUST preserve project overlay keys (board, environments, globs, `overlay_doc`) and refresh nucleus/skins/helpers + `pin`. v1 MUST NOT use submodule, native marketplace, or template-clone as the primary channel. Skill `implantar` text SHALL list the fourth skin `.dsh/`.

#### Scenario: Pin materializes nucleus skins helpers in consumer git
- **WHEN** overlay is valid and `implantar --pin v1.1.0` completes
- **THEN** `.cursor/`, `.grok/`, `.opencode/`, and `.dsh/` exist in the consumer
- **AND** `scripts/process-fsm/` (overlay-reading Guard) exists in the consumer
- **AND** `.agents/skills/` for impeccable, design-critic, and playwright-cli exist
- **AND** helpers and generated `AGENTS.md` exist
- **AND** those trees are committed in that consumer git
- **AND** overlay contains `pin: v1.1.0`
- **AND** stubs are at most 8 non-empty body lines
- **AND** `.grok/`, `.opencode/`, and `.dsh/` contain no T0–T17 or I1–I9 table

#### Scenario: Pin copies .dsh even without clients.dsh
- **WHEN** overlay has no `clients.dsh` key and `--pin v1.1.0` completes
- **THEN** `.dsh/` is still copied
- **AND** overlay validation does not raise `OverlayInvalid` for the missing key

#### Scenario: Bump is re-implant plus commit
- **WHEN** the consumer moves pin from `v1.0.1` to `v1.1.0`
- **THEN** nucleus, skins including `.dsh/`, and helpers are copied again and the diff is committed
- **AND** board, environments, globs, and `overlay_doc` are not reset to template empties

#### Scenario: Submodule is not the v1 channel
- **WHEN** a consumer is implanted on v1
- **THEN** `.cursor/` is not a git submodule pointer as the primary install
- **AND** skins are not gitignored

### Requirement: Four adapters ship in every consumer
Every implanted consumer SHALL receive the Cursor adapter (`.cursor/hooks.json` `sessionStart`, `preToolUse` failClosed, `beforeShellExecution`, `afterFileEdit`/`stop` Impeccable, `harness.mdc`, `/opsx-*` commands), the Grok adapter (`.grok/hooks/` `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`), the OpenCode 1.18.18 adapter (`.opencode/plugin/` `tool.execute.before` throw on deny, `experimental.chat.system.transform`, `tool.execute.after` + `session.idle` fail-open), and the dsh adapter (`.dsh/plugin/` `tools/pre-execute` `{ kind: 'deny' }` fail-closed, `systemPrompt.section` Moore, `tools/post-execute` + `agent/turn-stopping` fail-open). Adapters SHALL translate only. Dual-write of T0–T17 / I1–I9 into `.grok/`, `.opencode/`, or `.dsh/` remains forbidden. Lock machine and `opencode.json` as model/MCP/permission contract remain forbidden. The fourth harness (dsh) MUST NOT be a source of law.

#### Scenario: Write product on integration branch denies on four clients
- **WHEN** Cripto is pinned in the card worktree and `q_git` is the integration branch
- **THEN** an illegal product Write is denied on Cursor, Grok Build, OpenCode 1.18.18, and dsh (plugin loaded)
- **AND** no adapter copy of T0–T17 exists

#### Scenario: Current Cripto skins stay until pin
- **WHEN** Apply has not yet committed the pin in consumer git
- **THEN** existing Cripto `.cursor/` `.grok/` `.opencode/` skins MUST NOT be deleted as a prelude
- **AND** they are replaced by implantar at pin, not deleted earlier
- **AND** `.dsh/` appears at pin, not before Pronto para Dev

## ADDED Requirements

### Requirement: clients.dsh is an optional extra not a schema break
Overlay schema major SHALL remain `1`. `CLIENT_KEYS` SHALL remain `("cursor", "grok", "opencode")`. Missing a `CLIENT_KEYS` entry SHALL remain `OverlayInvalid`. Extra keys under `clients` (including `dsh`) SHALL be accepted. Apply MUST NOT start rejecting unknown `clients.*` keys (that would break the Cripto pin write while keeping `SCHEMA_MAJOR=1`). `clients.dsh` SHALL NOT be required. `empty_template` / `install.sh --init` MUST NOT emit `clients.dsh`. `install.sh --pin` MUST NOT inject `clients.dsh` into an overlay that omits the key. Cripto Apply SHALL write `clients.dsh.auto: false` as a consumer overlay edit. Absence of `clients.dsh` MUST NOT disable the copied `.dsh/` Guard. Clara/Hermes MUST NOT be implanted by this change.

#### Scenario: Overlay without clients.dsh validates
- **WHEN** `validate_overlay` runs on a filled overlay that has `clients.cursor`, `clients.grok`, and `clients.opencode` and omits `clients.dsh`
- **THEN** validation passes
- **AND** it does not raise `OverlayInvalid`

#### Scenario: Overlay with extra clients.dsh auto false validates
- **WHEN** `validate_overlay` runs on a filled overlay that has `clients.cursor`, `clients.grok`, `clients.opencode`, and extra `clients.dsh.auto: false`
- **THEN** validation passes (positive extra; witnesses the Cripto pin write)
- **AND** it does not raise `OverlayInvalid`
- **AND** Apply MUST NOT start rejecting unknown `clients.*` keys while `SCHEMA_MAJOR` remains 1

#### Scenario: Init template omits clients.dsh
- **WHEN** `implantar --init` writes a new overlay template
- **THEN** `clients` lists only `cursor`, `grok`, and `opencode`
- **AND** `clients.dsh` is absent

#### Scenario: Pin does not inject the key
- **WHEN** `--pin v1.1.0` runs on an overlay that omitted `clients.dsh`
- **THEN** the overlay still omits `clients.dsh` after pin
- **AND** `.dsh/` is copied anyway

#### Scenario: Cripto records auto false
- **WHEN** Cripto Apply of this change finishes the pin
- **THEN** overlay contains `clients.dsh.auto: false`
- **AND** `SCHEMA_MAJOR` in `overlay.py` is still 1
- **AND** `CLIENT_KEYS` is still three names
