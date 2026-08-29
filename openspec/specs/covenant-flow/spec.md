# covenant-flow Specification

## Purpose
TBD - created by archiving change card-773-covenant-flow. Update Purpose after archive.
## Requirements
### Requirement: Product repository is oalansilva/covenant-flow
The portable process product SHALL live in the private GitHub repository `oalansilva/covenant-flow` (display name Covenant Flow). The nucleus SHALL be `process-fsm.yaml`, `scripts/process-fsm/` (`guard`, `resolve`, `process_event`, `paging`, goldens), and the canonical skill files. Product and skill names MUST NOT contain `alan`. The product MUST NOT ship Funil Cripto copy, `PRODUCT.md` / `DESIGN.md` / token-sheet content, or PostgreSQL as an always-on of the package.

#### Scenario: Fresh clone of the product repo
- **WHEN** a machine clones `oalansilva/covenant-flow`
- **THEN** the tree contains the nucleus, the 20 canonical skills, three client adapters, `install.sh`, and the overlay template
- **AND** no skill directory or product name contains `alan`
- **AND** no Funil Cripto or token-sheet brand content is in the package

#### Scenario: Host trial folder is not a product artifact
- **WHEN** a reviewer inspects the product repository and this OpenSpec change
- **THEN** `/home/ubuntu/covenant-flow-trial` is not shipped, committed, or cited as a canonical artifact
- **AND** host backup SHA `94f8ed41` is not a product restore requirement

### Requirement: Overlay machine file is .covenant-flow/overlay.yaml
Each consumer SHALL keep machine parameters in `.covenant-flow/overlay.yaml`. Human overlay prose SHALL live at the path in `overlay_doc` (Cripto: `docs/crypto-overlay.md`) and MUST NOT replace the yaml. Missing or invalid overlay SHALL fail closed (Guard deny of product writes; `implantar --pin` refuses). `implantar --init` SHALL write a template with required keys present and empty and MUST NOT guess project values.

#### Scenario: Init lists empty required keys
- **WHEN** `implantar --init` runs in a target repo without an overlay
- **THEN** `.covenant-flow/overlay.yaml` exists from the template
- **AND** the skill lists required keys that are still empty
- **AND** it does not fill board ids, globs, or environments from Cripto defaults

#### Scenario: Pin without valid overlay is denied
- **WHEN** `implantar --pin v1.2.3` runs and the overlay is missing a required key or fails schema
- **THEN** the command exits non-zero
- **AND** consumer skins are not half-applied as the success path

#### Scenario: Human overlay_doc stays per project
- **WHEN** Cripto is implanted
- **THEN** `overlay_doc` is `docs/crypto-overlay.md`
- **AND** the machine file is `.covenant-flow/overlay.yaml`
- **AND** `docs/crypto-overlay.md` is not the product-wide overlay path

### Requirement: Overlay schema carries board repo globs pin and two-path
The overlay schema SHALL require `board.owner`, `board.number`, `board.status_field_id`, `board.status_options` (column **names** MUST equal the 12 names in `process-fsm.yaml`; **ids** are Project v2), `repo`, `product_globs`, `design_globs`, `integration_branch`, `production_branch`, `pin`, `canonical_paths`, `forbidden_worktrees`, `overlay_doc`, `clients`, Impeccable paths, and `runtime.playwright`. `environments.dev` SHALL be required when the project has a DEV runtime; `environments.prod` MAY be omitted. Each environment object SHALL carry `source`, `url`, `db`, `services[]`. `release.{restart,migrate,build,health_url}` SHALL be present; empty production hooks SHALL cause T16 to refuse deploy. `runtime.database` MAY be omitted. A breaking overlay-schema change SHALL bump the product major (`v2.0.0`). Law tables T0–T17 and I1–I9 MUST NOT appear in the overlay.

#### Scenario: Schema break is a major tag
- **WHEN** a required overlay key is removed or renamed incompatibly
- **THEN** the published product tag increments major (`v2.0.0`)
- **AND** a minor or patch tag is not used for that break

#### Scenario: Project without PROD omits environments.prod
- **WHEN** overlay has `environments.dev` and no `environments.prod`
- **THEN** `covenant-flow-environments` assumes DEV
- **AND** it refuses production deploy
- **AND** T16 refuses deploy when release hooks are empty

#### Scenario: Overlay does not copy the law table
- **WHEN** a reviewer inspects `.covenant-flow/overlay.yaml`
- **THEN** it has no T0–T17 table and no I1–I9 list
- **AND** column **names** in `board.status_options` match the yaml law

### Requirement: board.status_options joins yaml names to Project v2 ids
Overlay `board.status_options` SHALL map each of the 12 column **names** from `process-fsm.yaml` to a Project v2 **id**. Validation SHALL join name→id. Overlay MUST NOT copy T0–T17 or I1–I9. Missing overlay, a name that does not match the yaml, or a missing id SHALL fail closed.

#### Scenario: Join succeeds when twelve names match yaml
- **WHEN** overlay `board.status_options` lists exactly the 12 yaml column names each with an id
- **THEN** overlay validation passes the join
- **AND** Guard Status-edit uses those ids, not a packaged Cripto field constant

#### Scenario: Name drift or missing id fails closed
- **WHEN** a `status_options` name is not one of the 12 yaml names, or an id is missing
- **THEN** overlay validation fails
- **AND** `implantar --pin` refuses
- **AND** Guard product writes deny

### Requirement: implantar copies nucleus adapters agents skills helpers and the consumer commits them
Skill `implantar` (Portuguese) plus `install.sh --pin` SHALL copy into the consumer: the nucleus (`process-fsm.yaml` and `scripts/process-fsm/`), the three adapters (`.cursor/`, `.grok/`, `.opencode/`), `.agents/skills/` (`impeccable`, `design-critic`, `playwright-cli`), helpers (`publish-openspec-card-artifacts.sh`, generic `release-guard`), and the template `AGENTS.md`. The consumer git SHALL commit those trees (not gitignore, not submodule pointers). On Cripto, which already has `scripts/process-fsm/`, pin SHALL update them to the overlay-reading Guard. The overlay SHALL record `pin` as a semver tag `vMAJOR.MINOR.PATCH`. Updating SHALL mean re-implantar plus commit of the diff. Bump MUST preserve project overlay keys (board, environments, globs, `overlay_doc`) and refresh nucleus/skins/helpers + `pin`. v1 MUST NOT use submodule, native marketplace, or template-clone as the primary channel.

#### Scenario: Pin materializes nucleus skins helpers in consumer git
- **WHEN** overlay is valid and `implantar --pin v1.2.3` completes
- **THEN** `.cursor/`, `.grok/`, and `.opencode/` exist in the consumer
- **AND** `scripts/process-fsm/` (overlay-reading Guard) exists in the consumer
- **AND** `.agents/skills/` for impeccable, design-critic, and playwright-cli exist
- **AND** helpers and generated `AGENTS.md` exist
- **AND** those trees are committed in that consumer git
- **AND** overlay contains `pin: v1.2.3`
- **AND** stubs are at most 8 non-empty body lines
- **AND** `.grok/` and `.opencode/` contain no T0–T17 or I1–I9 table

#### Scenario: Bump is re-implant plus commit
- **WHEN** the consumer moves pin from `v1.2.3` to `v1.3.0`
- **THEN** nucleus, skins, and helpers are copied again and the diff is committed
- **AND** board, environments, globs, and `overlay_doc` are not reset to template empties

#### Scenario: Submodule is not the v1 channel
- **WHEN** a consumer is implanted on v1
- **THEN** `.cursor/` is not a git submodule pointer as the primary install
- **AND** skins are not gitignored

### Requirement: Canonical skill set is twenty names without alan
The product SHALL ship exactly these operational skills: `covenant-flow` (formerly `alan-workflow`), `covenant-flow-environments` (formerly `alan-workflow-ambientes`), `grill-card`, `grilling`, `openspec-new-change`, `openspec-ff-change`, `openspec-apply-change`, `openspec-verify-change`, `openspec-archive-change`, `openspec-bulk-archive-change`, `openspec-continue-change`, `openspec-explore`, `openspec-onboard`, `openspec-sync-specs`, `github-project-board`, `kaizen`, `design-critic`, `impeccable`, `playwright-cli`, and `implantar`. After unique pin, the consumer git SHALL use only the new names (stubs/aliases of `alan-workflow*` MAY exist only until that unique pin).

#### Scenario: Product skills have no alan names
- **WHEN** the product skill directories are listed
- **THEN** `covenant-flow` and `covenant-flow-environments` exist
- **AND** `implantar` exists
- **AND** the ten `openspec-*` directories named in this requirement exist
- **AND** no `alan-workflow` or `alan-workflow-ambientes` directory exists in the product

#### Scenario: Cripto after unique pin uses new names
- **WHEN** Cripto git has been uniquely pinned
- **THEN** operational runbooks load `covenant-flow` and `covenant-flow-environments`
- **AND** `alan-workflow*` remain only if still in the alias window before unique pin, then only the new names

### Requirement: Three adapters ship in every consumer
Every implanted consumer SHALL receive the Cursor adapter (`.cursor/hooks.json` `sessionStart`, `preToolUse` failClosed, `beforeShellExecution`, `afterFileEdit`/`stop` Impeccable, `harness.mdc`, `/opsx-*` commands), the Grok adapter (`.grok/hooks/` `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`), and the OpenCode 1.18.18 adapter (`.opencode/plugin/` `tool.execute.before` throw on deny, `experimental.chat.system.transform`, `tool.execute.after` + `session.idle` fail-open). Adapters SHALL translate only. Dual-write of T0–T17 / I1–I9 into `.grok/` or `.opencode/` remains forbidden. Lock machine and `opencode.json` as model/MCP/permission contract remain forbidden. A fourth harness MUST NOT be a source of law.

#### Scenario: Write product on integration branch denies on three clients
- **WHEN** Cripto is pinned in the card worktree and `q_git` is the integration branch
- **THEN** an illegal product Write is denied on Cursor, Grok Build, and OpenCode 1.18.18
- **AND** no adapter copy of T0–T17 exists

#### Scenario: Current Cripto skins stay until pin
- **WHEN** Apply has not yet committed the pin in consumer git
- **THEN** existing Cripto `.cursor/` `.grok/` `.opencode/` skins MUST NOT be deleted as a prelude
- **AND** they are replaced by implantar at pin, not deleted earlier

### Requirement: Apply pins Cripto in the worktree and does not live-switch the host
Creating the GitHub product repository and pinning Cripto SHALL happen only while card #773 has `Status=Pronto para Dev`. Apply SHALL (a) build the product tree out of band, (b) fill Cripto `.covenant-flow/overlay.yaml` while this worktree still uses the current yaml-globs Guard, (c) then `implantar --pin` **and** switch Guard/`page()` to overlay in the **same** pin commit. Empty overlay mid-Apply is not a success path; `--init` on Cripto MUST be followed immediately by filling required keys before enabling fail-closed overlay Guard. The pin commit SHALL include `.cursor/`, `.grok/`, `.opencode/`, overlay, `scripts/process-fsm/`, `.agents/skills/` (`impeccable`, `design-critic`, `playwright-cli`), and generated `AGENTS.md`. Apply MUST NOT switch this machine's day-to-day Cursor/Grok/OpenCode from `alan-workflow*` to `covenant-flow*`. Live host rename SHALL happen only after #773 `Status=Pronto` (T16 / published lote). Until Pronto, live host stays `alan-workflow` and new names exist only in sandbox or in the pinned worktree git.

#### Scenario: Apply ends with product repo and Cripto pin in worktree
- **WHEN** Apply of #773 finishes the card worktree
- **THEN** GitHub repo `oalansilva/covenant-flow` exists
- **AND** Cripto in that worktree is pinned (nucleus + skins + `.agents/skills/` + helpers + overlay `pin` + overlay-reading Guard in that git)
- **AND** the live host still loads `alan-workflow*` while #773 is not Pronto

#### Scenario: Overlay is filled before fail-closed Guard
- **WHEN** Apply is mid-flight in this Cripto worktree
- **THEN** Guard still classifies against yaml globs until the pin commit
- **AND** `.covenant-flow/overlay.yaml` is filled and valid before that pin commit
- **AND** empty overlay plus overlay-reading fail-closed Guard is not a success path

#### Scenario: Live switch is not Pronto para Dev
- **WHEN** #773 is `Pronto para Dev` or Apply is running
- **THEN** `~/.cursor/skills/alan-workflow*` and the live day-to-day names MUST NOT be renamed
- **AND** live switch waits for `Status=Pronto`

#### Scenario: Fresh snapshot before live mutation
- **WHEN** #773 reaches `Status=Pronto` and live host rename runs
- **THEN** a fresh snapshot of the live tree (prefer `develop`) was taken before mutation
- **AND** backup SHA `94f8ed41` is not the restore of that switch
- **AND** afterwards the host uses `covenant-flow*`

### Requirement: Review stance lives in local reviewers not BUGBOT.md
The product SHALL version `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` with `inherit` and `readonly`. Review constraints SHALL live in those files. `REVIEW.md` MAY exist in a consumer and MUST NOT mention Bugbot. The product MUST NOT ship `.cursor/BUGBOT.md` or nested homonyms and MUST NOT use Cursor Bugbot (`/review-bugbot`) as Code Review. Code Review gate SHALL be `diff-reviewer` plus `code-reviewer`. `/review-security` MAY run when Alan explicitly asks.

#### Scenario: Product has no BUGBOT.md
- **WHEN** the product tree and a uniquely pinned Cripto tree are listed
- **THEN** no `BUGBOT.md` exists (root or nested)
- **AND** `diff-reviewer.md` and `code-reviewer.md` exist with `readonly: true` and `model: inherit`

#### Scenario: Optional REVIEW.md has no Bugbot
- **WHEN** a consumer adds `REVIEW.md`
- **THEN** that file does not mention Bugbot
- **AND** Code Review gate remains the two local reviewers
- **AND** `/review-security` MAY run only when Alan explicitly asks

### Requirement: Generic AGENTS template and release-guard travel with the product
The product SHALL ship a template root `AGENTS.md` (tuple `(q, bound_card, q_git)`, chat wording is not δ, board URL generated from overlay `board.owner` and `board.number`, at most 40 non-empty lines, overlay on-demand via `overlay_doc`). Two-path SHALL be overlay `canonical_paths` / `forbidden_worktrees`, not hardcoded Cripto filesystem paths in the package. `publish-openspec-card-artifacts.sh` SHALL ship. Release-guard SHALL be generic: T16 checklist plus overlay hooks `restart` / `migrate` / `build` / `health_url`.

#### Scenario: Template AGENTS.md does not hardcode Cripto overlay path as the product path
- **WHEN** the product template `AGENTS.md` is rendered for a consumer
- **THEN** it points at that consumer's `overlay_doc`
- **AND** it contains a board URL derived from overlay board fields
- **AND** it states chat is not δ

#### Scenario: Release-guard uses overlay hooks
- **WHEN** T16 runs for a consumer with empty `release.*` production hooks
- **THEN** deploy is refused
- **AND** the packaged guard does not call Cripto systemd unit names hardcoded as the only path

### Requirement: Host evidence is not a product requirement
Paths, SHAs, and restore notes of this operator machine in issue #773 SHALL remain host-only. Design and Apply MAY read them. They MUST NOT become acceptance criteria of `oalansilva/covenant-flow`.

#### Scenario: Product README does not require host backup paths
- **WHEN** the product repository is reviewed for portability
- **THEN** it does not require `/home/ubuntu/backups/covenant-flow-pre-773-*` or SHA `94f8ed41` to install
- **AND** it installs from the GitHub repo plus `implantar --pin`

### Requirement: Product README orients a stranger in PT-BR before install
The product repository `oalansilva/covenant-flow` SHALL ship a single root `README.md` written in PT-BR. The README MUST explain, **before** any clone or `install.sh` block: what Covenant Flow is, who uses it, nucleus versus consumer versus overlay, that canal v1 is copy-and-commit in the consumer git, and that the first consumer is Cripto (`oalansilva/crypto`). Clone MUST NOT be the first paragraph. The product README MUST NOT require host backup paths. The product MUST NOT add a second install file (`CONTRIBUTING.md` or `docs/` install) as part of this orientation.

#### Scenario: Fresh clone visitor reads the README top-down
- **WHEN** a visitor opens the product `README.md` from a fresh clone of `oalansilva/covenant-flow` without opening skill `covenant-flow`
- **THEN** the file is in PT-BR
- **AND** before any clone or `install.sh --init` / `--pin` block it explains what the product does, who uses it, nucleus versus consumer versus overlay, and canal v1
- **AND** the clone command is not the first paragraph
- **AND** there is no `CONTRIBUTING.md` or second install file added by this change
- **AND** the README does not require `/home/ubuntu/backups/covenant-flow-pre-773-*` or SHA `94f8ed41` to install

### Requirement: Product README lists four clients and Auto versus cooperative
The stranger block of the product README SHALL name Cursor, Grok, OpenCode, and dsh. It SHALL state that Auto is Cursor overlay `clients.cursor.auto: true` (the client MAY run without a per-tool permission prompt) and that Auto does **not** authorize crossing columns. It SHALL state that Grok, OpenCode, and dsh are cooperative (`clients.*.auto: false`) until a deny essay PASS on the integration branch. The README MUST NOT claim Auto on Grok, OpenCode, or dsh.

#### Scenario: Stranger block names clients and Auto versus cooperative
- **WHEN** a visitor reads the client portion of the product README
- **THEN** Cursor, Grok, OpenCode, and dsh appear by name
- **AND** Auto (Cursor) is distinguished from cooperative (the other three, until deny essay PASS)
- **AND** the text states that Auto does not authorize crossing columns

### Requirement: Product README walkthrough is one line per column plus one human-gates sentence
The product README SHALL walk through all twelve `process-fsm.yaml` column names in PT-BR, including `Cancelado` as terminal, at **one line per column** (name + meaning). It SHALL include **exactly one** sentence for the three human gates: Alan prioritizes Em Refinamento→Todo; only Alan Aprovação de Design→Pronto para Dev; Alan homologates Done→Homologado. That sentence MUST NOT contain T0–T17 identifiers. The README MUST NOT include a T0–T17 / I1–I9 table, a paragraph per column, or hooks / OpenSpec order / release playbook. Skill `covenant-flow` remains the operator runbook.

#### Scenario: Walkthrough has twelve PT-BR lines and one gates sentence
- **WHEN** a visitor counts the column walkthrough in the product README
- **THEN** there are the twelve yaml names including `Cancelado` as terminal, one line each, names in PT-BR
- **AND** there is exactly one sentence of the three human gates without T0–T17 identifiers
- **AND** there is no T0–T17 / I1–I9 table and no hooks / OpenSpec / release playbook

### Requirement: GitHub repository description is the frozen PT-BR sentence
The GitHub repository `oalansilva/covenant-flow` description SHALL be exactly `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`. That string SHALL ship in the same deliverable as the PT-BR README. LICENSE and GitHub homepage MUST NOT be changed by this requirement.

#### Scenario: Repo page shows the frozen description
- **WHEN** a visitor reads the GitHub description of `oalansilva/covenant-flow` after this deliverable
- **THEN** the description is exactly `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`
- **AND** it replaces the English description `Covenant Flow — portable 12-column process (nucleus + adapters)`

### Requirement: Pin example is the deliverable tag and pin does not copy README
The operator section of the product README SHALL document `--init` / `--pin` / Layout in PT-BR **after** the stranger and walkthrough blocks. The `--pin` example MUST be the semver tag of the commit that ships that README (this deliverable: `v1.1.2`; a later tagged README MUST update the example to that new tag). The example MUST NOT be `latest` or an unnumbered placeholder. `install.sh --pin` MUST NOT copy product `README.md` into the consumer. Overlay schema, `install.sh` copy list, skills, hooks, yaml, generated `AGENTS.md`, and adapters MUST NOT be rewritten as part of this documentation change.

#### Scenario: Operator section follows the stranger and uses the deliverable tag
- **WHEN** a visitor who already understood the product scrolls to Install / Pin / Layout
- **THEN** those sections are in PT-BR
- **AND** the `--pin` example is the deliverable tag (`v1.1.2` for this change)

#### Scenario: Pin still does not copy README into the consumer
- **WHEN** overlay is valid and `implantar --pin` completes on a consumer
- **THEN** the consumer tree does not receive a copy of the product `README.md` as a pin payload file
- **AND** #773 and #784 remain closed as a consequence of this change

