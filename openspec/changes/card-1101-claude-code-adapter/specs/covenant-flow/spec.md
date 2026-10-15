## MODIFIED Requirements

### Requirement: implantar copies nucleus adapters agents skills helpers and the consumer commits them
Skill `implantar` (Portuguese) plus `install.sh --pin` SHALL copy into the consumer the nucleus (`process-fsm.yaml`, `scripts/process-fsm/`), five adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`, `.codex/`), `.agents/skills/` (Impeccable, design-critic, playwright-cli and Codex bridges), helpers (`publish-openspec-card-artifacts.sh`, generic `release-guard`, dsh boot helper), and the template `AGENTS.md`. `install.sh --pin` SHALL copy `.dsh/` and `.codex/` **always**, independent of optional `clients.*` overlay entries. Existing unrelated Codex hooks and Impeccable provider files MUST be preserved or an unsafe conflict MUST fail visibly. For `.cursor/model-map.yaml`, the pin SHALL read the **target consumer file** at installation time, preserve top-level `juizo.label/slug`, `execucao.label/slug`, and every `forbid` entry, and add only the Codex subblocks; a local conflict MUST cause visible refusal or an explicit inspected merge, never silent overwrite from the product or Design worktree. The consumer git SHALL commit those trees (not gitignore, not submodule pointers). On Cripto, which already has `scripts/process-fsm/`, pin SHALL update them to the overlay-reading Guard. The overlay SHALL record `pin` as a semver tag `vMAJOR.MINOR.PATCH`. Updating SHALL mean re-implantar plus commit of the diff. Bump MUST preserve project overlay keys (board, environments, globs, `overlay_doc`) and refresh nucleus/skins/helpers + `pin`. v1 MUST NOT use submodule, native marketplace, or template-clone as the primary channel. Exception, only for hook registration (Alan's decision of 2026-10-14): from the account-registration pin onward, `install.sh --pin` MUST NOT write Covenant Flow hook registrations for Claude Code, Cursor, Codex or OpenCode into the consumer and SHALL remove only Covenant Flow entries from their existing project registrations (`.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`, auto-loaded `.opencode/plugin/`) while preserving foreign entries; the Grok Build and dsh registrations (`.grok/hooks/process-fsm.json`, `.dsh/cordis.patch.yml`) SHALL keep being copied as before this change; it SHALL write the adapter manifest (registration mode, shim protocol, per-client adapter entry and file list). The registration itself is installed in the operator account by `install.sh --account` through the `account-hook-shim`; that channel MUST NOT carry FSM, adapters, skills or policy.

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
- **WHEN** a consumer has a conflicting or malformed `.codex/hooks.json` (or another project registration) from which Covenant Flow entries cannot be removed without loss
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

#### Scenario: Pin leaves no hook registration in the consumer
- **WHEN** a consumer moves to the account-registration pin
- **THEN** its Claude Code, Cursor, Codex and OpenCode project registration files keep only foreign entries and the adapter manifest is committed
- **AND** those four clients' hook registration is available only through `install.sh --account` in the operator account
- **AND** the Grok Build and dsh project registrations are the same as on the previous pin
