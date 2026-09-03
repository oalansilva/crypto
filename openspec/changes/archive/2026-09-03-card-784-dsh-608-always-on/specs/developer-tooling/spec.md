## ADDED Requirements

### Requirement: dsh boot fails closed when canonical_paths.dev is set and is not a directory
`scripts/process-fsm/dsh_boot.sh` SHALL still prefer overlay `canonical_paths.dev` as `LAUNCH_DIR` when that value is a non-empty path **and** that path is an existing directory (then `dsh web --patch` from there). When the overlay key is missing or empty, `LAUNCH_DIR` MUST be `REPO_ROOT`. When the key is non-empty and the path is **not** a directory, the helper MUST exit non-zero and MUST print the path in the error message. The boot helper MUST NOT set the dsh GUI session workspace/cwd; always-on ingest MUST remain the Guard plugin's responsibility. `dsh plugin add` remains not the v1 pin channel. Absolute plugin `name`s in the materialized patch are unchanged.

#### Scenario: Empty canonical_paths.dev launches from REPO_ROOT
- **WHEN** overlay `canonical_paths.dev` is absent or an empty string and `dsh_boot.sh` runs
- **THEN** `LAUNCH_DIR` is the consumer `REPO_ROOT`
- **AND** the process does not exit solely because the key is empty

#### Scenario: Non-directory canonical_paths.dev fails
- **WHEN** overlay `canonical_paths.dev` is a non-empty path that does not exist or is not a directory
- **THEN** `dsh_boot.sh` exits with status ≠ 0
- **AND** stderr names that path

#### Scenario: Directory canonical_paths.dev still preferred
- **WHEN** overlay `canonical_paths.dev` is an existing directory
- **THEN** `LAUNCH_DIR` is that directory
- **AND** `dsh web --patch` is still invoked with absolute plugin names

### Requirement: dsh developer tooling publishes process skills from the plugin provider
A pinned consumer's dsh adapter SHALL register a `ctx.skills` provider from `.dsh/plugin/process-fsm-guard.js` over `REPO_ROOT/.dsh/skills` so process skill stubs are in the model catalog when session cwd is not the git root. The provider's `list`/`get` MUST be thenables and MUST satisfy live `validateCandidate` (`candidate.provider` equals the provider `name`). Versioned `.dsh/cordis.patch.yml` MUST NOT gain skill directory paths or `customSkillDirs`. Host row `skill-filesystem` `disabled: true` MUST NOT be modified. Native preset skill discovery MUST stay. Goldens in `pytest scripts/process-fsm` MUST cover the agents paging section (looked up by name, not `sections[0]`), the skill provider listing `covenant-flow` with lookup cwd ≠ repo **and** a non-aborted `signal` via a fake `waitWithAbort`/`validateCandidate` path, and the boot exit on a bad `canonical_paths.dev`.

#### Scenario: Golden covers catalog provider off-repo cwd
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** a fixture lists `covenant-flow` from the plugin provider with lookup cwd outside the consumer git
- **AND** that fixture passes a `signal` into `list`/`get` and asserts each candidate `provider` field
- **AND** no network call to GitHub is made

#### Scenario: Patch yaml has no skill roots
- **WHEN** `.dsh/cordis.patch.yml` is inspected after this change
- **THEN** it still only inserts the Guard and Impeccable plugin modules
- **AND** it does not mention `.dsh/skills` as a loader path
