# covenant-flow Specification

## Purpose
TBD - created by archiving change card-773-covenant-flow. Update Purpose after archive.
## Requirements
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
Skill `implantar` (Portuguese) plus `install.sh --pin` SHALL copy into the consumer: the nucleus (`process-fsm.yaml` and `scripts/process-fsm/`), the four adapters (`.cursor/`, `.grok/`, `.opencode/`, `.dsh/`), `.agents/skills/` (`impeccable`, `design-critic`, `playwright-cli`), helpers (`publish-openspec-card-artifacts.sh`, generic `release-guard`, dsh boot helper), and the template `AGENTS.md`. `install.sh --pin` SHALL copy `.dsh/` **always**, including when overlay omits `clients.dsh`. The consumer git SHALL commit those trees (not gitignore, not submodule pointers). On Cripto, which already has `scripts/process-fsm/`, pin SHALL update them to the overlay-reading Guard. The overlay SHALL record `pin` as a semver tag `vMAJOR.MINOR.PATCH`. Updating SHALL mean re-implantar plus commit of the diff. Bump MUST preserve project overlay keys (board, environments, globs, `overlay_doc`) and refresh nucleus/skins/helpers + `pin`. v1 MUST NOT use submodule, native marketplace, or template-clone as the primary channel.

#### Scenario: Pin materializes nucleus skins helpers in consumer git
- **WHEN** overlay is valid and `implantar --pin v1.2.3` completes
- **THEN** `.cursor/`, `.grok/`, `.opencode/`, and `.dsh/` exist in the consumer
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
The stranger block of the product README SHALL name Cursor, Grok, OpenCode, and dsh. It SHALL state that the four clients are cooperative. It SHALL state that Cursor is cooperative by contract and that Grok, OpenCode, and dsh remain cooperative until a deny essay PASS on the integration branch. It SHALL state that overlay `clients.*.auto` is a machine claim and does **not** drive the `AGENTS.md` stub. It SHALL state that Auto does **not** authorize crossing columns. The README MUST NOT claim that Auto is Cursor overlay `clients.cursor.auto: true`. The README MUST NOT claim Auto on Grok, OpenCode, or dsh. The README MUST NOT mention IDE/CLI `approvalMode` or Run Everything.

#### Scenario: Stranger block names four cooperative clients
- **WHEN** a visitor reads the client portion of the product README
- **THEN** Cursor, Grok, OpenCode, and dsh appear by name
- **AND** the text states that the four are cooperative
- **AND** the text does not state that Auto is Cursor `clients.cursor.auto: true`
- **AND** the text states that Auto does not authorize crossing columns
- **AND** the text does not claim Auto on Grok, OpenCode, or dsh

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
The operator section of the product README SHALL document `--init` / `--pin` / Layout in PT-BR **after** the stranger and walkthrough blocks. The `--pin` example MUST be the semver tag of the commit that ships that README (this deliverable: `v1.1.5`; a later tagged README MUST update the example to that new tag). The example MUST NOT be `latest` or an unnumbered placeholder. `install.sh --pin` MUST NOT copy product `README.md` into the consumer. This change SHALL rewrite `render_agents()` and therefore the generated `AGENTS.md`. Overlay schema, `install.sh` copy list, skills, hooks, yaml law, Guard, and adapters MUST NOT be rewritten as part of this change. #787 MUST NOT be reopened as Apply.

#### Scenario: Operator section follows the stranger and uses the deliverable tag
- **WHEN** a visitor who already understood the product scrolls to Install / Pin / Layout
- **THEN** those sections are in PT-BR
- **AND** the `--pin` example is the deliverable tag (`v1.1.5` for this change)

#### Scenario: Pin still does not copy README into the consumer
- **WHEN** overlay is valid and `implantar --pin` completes on a consumer
- **THEN** the consumer tree does not receive a copy of the product `README.md` as a pin payload file
- **AND** #773, #784, and #787 are not reopened as Apply as a consequence of this change

### Requirement: render_agents hardcodes four cooperative clients
`render_agents()` SHALL hardcode four cooperative clients. The generated stub MUST contain exactly these two client lines, in this order: `Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).` and `Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.` The function MUST NOT interpolate overlay `clients.*.auto`. The stub MUST NOT contain `Auto permitido`. The stub MUST NOT claim Auto Grok, Auto OpenCode, or Auto dsh. The deny-essay clause MUST apply only to Grok, OpenCode, and dsh. Cursor is cooperative by contract, not by a pending essay. The stub MUST remain at most 40 non-empty lines. `SCHEMA_MAJOR` SHALL remain `1`. `CLIENT_KEYS` SHALL remain `("cursor", "grok", "opencode")`.

#### Scenario: Generated stub is four cooperative clients
- **WHEN** `render_agents()` runs after this change
- **THEN** the text names Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it does not contain `Auto permitido`
- **AND** it does not contain Auto Grok, Auto OpenCode, or Auto dsh
- **AND** the deny-essay phrase applies only to Grok, OpenCode, and dsh
- **AND** overlay `clients.cursor.auto: true` in a fixture does not change the stub text

#### Scenario: Pin regenerates AGENTS.md from the new hardcode
- **WHEN** `implantar --pin` of this change's product tag completes on Cripto
- **THEN** consumer `AGENTS.md` matches the new `render_agents()` output
- **AND** `Auto permitido` is absent
- **AND** the stub was not hand-edited as the success path

### Requirement: Cripto overlay cooperative claim is false without schema break
Cripto overlay SHALL record `clients.cursor.auto: false` (grok, opencode, and dsh remain `false`). `validate_overlay` SHALL still accept that overlay (`SCHEMA_MAJOR` 1, `CLIENT_KEYS` three, extra `dsh` allowed) and MUST NOT start reading the `auto` boolean as a stub or Guard switch. This change's product tag SHALL be a patch (expected `v1.1.5`; Apply confirms origin has no newer tag, else the next unused patch). Apply MUST NOT change Guard, T0–T17, local Cursor IDE/CLI config, or Cripto `backend/**` / `frontend/src/**`.

#### Scenario: Overlay with four auto false validates
- **WHEN** `validate_overlay` runs on Cripto overlay with `clients.cursor.auto: false` and the other three `false`
- **THEN** validation passes
- **AND** `SCHEMA_MAJOR` is 1
- **AND** `CLIENT_KEYS` remains three names
- **AND** extra `clients.dsh.auto: false` is still accepted

### Requirement: Grill-card section names the operator language ceiling
`.cursor/skills/covenant-flow/SKILL.md` SHALL include, in the `## Grill-card` section, this exact sentence in addition to the existing host-options relay line:

`Tecto: Qs e options em português de operador em todo card em Em Refinamento; identificador do git é facto no body ou *como* no Design, não option no host; Other vazio, silêncio e «não percebi» / «isto é técnico» reclassificam e nunca aceitam a recomendada.`

The existing offer-grill trigger (body lacks the six DoD sections) and the parent relay of **all** `options[]` (MUST NOT collapse to the recommended) SHALL remain in that section. This requirement MUST NOT add a FSM state, event, hook, or `enabled_tools` entry, MUST NOT edit `process-fsm.yaml` as a side effect of this sentence, and MUST NOT name the host tool in `.grok/skills/*` stubs.

#### Scenario: Grill-card block names the ceiling besides relay
- **WHEN** a contributor reads the `## Grill-card` section of `.cursor/skills/covenant-flow/SKILL.md`
- **THEN** that section SHALL contain the exact ceiling sentence (Other vazio, silêncio, «não percebi»)
- **AND** it SHALL still contain the parent relay of all options (`todas as options` / `não colapsa`)
- **AND** the offer-grill trigger SHALL still be body without the six DoD sections

#### Scenario: No FSM change for the ceiling line
- **WHEN** this change is applied
- **THEN** `process-fsm.yaml` law table is unchanged by the ceiling sentence
- **AND** `AGENTS.md` always-on does not grow with this rule

### Requirement: Operator ceiling ships as product patch pin
This change SHALL ship in product `oalansilva/covenant-flow` as tag **`v1.1.6`** (patch; not a schema major), unless that tag is already taken on origin — in which case Apply SHALL use the next unused patch tag and MUST NOT bump major. `SCHEMA_MAJOR` SHALL remain 1. Apply SHALL commit the canonical `grill-card` ceiling, the exact Grill-card sentence in `covenant-flow`, and goldens in `scripts/process-fsm/test_grill_card.py` in the product first, then `implantar --pin` of that tag on Cripto. Overlay SHALL record `pin` as that tag. Client skins under `.grok/` `.dsh/` `.opencode/` for `grill-card` MUST stay at most 8 non-empty body lines.

#### Scenario: Pin materializes the ceiling on Cripto
- **WHEN** overlay is valid and `implantar --pin` of this card's tag completes on Cripto
- **THEN** `.cursor/skills/grill-card/SKILL.md` contains the operator-language ceiling
- **AND** the `## Grill-card` section of `covenant-flow` contains the exact ceiling sentence
- **AND** overlay contains `pin: v1.1.6` or the next unused patch tag Apply confirmed on origin
- **AND** grill-card stubs under `.grok/` `.dsh/` `.opencode/` remain at most 8 non-empty body lines

### Requirement: QA closeout runbook is client-labeled
`.cursor/skills/covenant-flow/SKILL.md` SHALL document QA closeout without adding a FSM state or event. Under the Cursor/Grok path it SHALL say: one isolated QA child reads checks and MUST NOT call `process_event`; the parent calls `aceitar_sha` only after a PR `q_git`→develop exists, then calls `integrar_develop` in the same turn as a green child, waits and retries on `qa-gate pending`, and treats `no_pr` / `sync: dirty` as visible causes. Under a dsh-labeled path it SHALL say: the runtime root MUST NOT spawn a QA child; the same turn MUST open the PR before T11, wait for `qa-gate`, and call T14 (Moore/plugin, not skill text alone). Stubs under `.dsh/skills/` and `.grok/skills/` MUST remain thin and MUST NOT copy the 12-column runbook. `AGENTS.md` MUST NOT grow for this rule.

#### Scenario: Cursor path keeps the QA child off process_event
- **WHEN** `covenant-flow` is read for the Cursor client
- **THEN** it says the QA child reads checks and MUST NOT call `process_event`
- **AND** it says the parent calls T14 in the same turn as a green child

#### Scenario: dsh path does not spawn a QA child
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says the root MUST NOT spawn a QA child
- **AND** it says the same turn opens the PR before T11, waits for `qa-gate`, and calls T14

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

### Requirement: Homologation residual pin v1.1.4 drops duplicate host-prompt recommendation
After origin `v1.1.3` (grill-root deny), this change SHALL ship product tag **`v1.1.4`** (patch; MUST NOT move `v1.1.3`). Canonical `grill-card` SHALL instruct that a live host prompt is title + conflict only; the recommendation SHALL appear only as the first option labelled `(Recommended)`. Apply SHALL `implantar --pin v1.1.4` on Cripto. Overlay SHALL record `pin: v1.1.4` and keep `clients.dsh.auto: false`. `SCHEMA_MAJOR` SHALL remain 1.

#### Scenario: Pin v1.1.4 refreshes grill-card host prompt copy on Cripto
- **WHEN** overlay is valid and `implantar --pin v1.1.4` completes on Cripto
- **THEN** overlay contains `pin: v1.1.4`
- **AND** `.cursor/skills/grill-card/SKILL.md` `## Cliente: dsh` after `_plain` contains `recomendação vive só` and `não copie`
- **AND** `clients.dsh.auto` remains `false`

### Requirement: clients.dsh is an optional extra not a schema break
Overlay schema major SHALL remain `1`. `CLIENT_KEYS` SHALL remain `("cursor", "grok", "opencode")`. Missing a `CLIENT_KEYS` entry SHALL remain `OverlayInvalid`. Extra keys under `clients` (including `dsh`) SHALL be accepted. `clients.dsh` SHALL NOT be required. `empty_template` / `install.sh --init` MUST NOT emit `clients.dsh`. `install.sh --pin` MUST NOT inject `clients.dsh` into an overlay that omits the key. Absence of `clients.dsh` MUST NOT disable the copied `.dsh/` Guard.

#### Scenario: Overlay without clients.dsh validates
- **WHEN** `validate_overlay` runs on a filled overlay that has `clients.cursor`, `clients.grok`, and `clients.opencode` and omits `clients.dsh`
- **THEN** validation passes
- **AND** it does not raise `OverlayInvalid`

#### Scenario: Overlay with extra clients.dsh auto false validates
- **WHEN** `validate_overlay` runs on a filled overlay that has extra `clients.dsh.auto: false`
- **THEN** validation passes
- **AND** `SCHEMA_MAJOR` remains 1
- **AND** `CLIENT_KEYS` is still three names

### Requirement: Follow-up pin v1.1.7 copies dsh reasoning-effort Guard
After the operator-ceiling pin `v1.1.6`, this change SHALL ship in product `oalansilva/covenant-flow` as the **next unused patch tag** after Apply checks origin (`v1.1.7` when that tag is free; not a schema major). Apply SHALL NOT bump major and SHALL NOT move `v1.1.6`. Sibling issue #818 (`card-818-dsh-grill-spawn-cite`, Status=Design) edits the same `dsh_plugin_lib.js` and Guard plugin and also hoped for `v1.1.7`; Apply SHALL rebase on the product tip so that card's haystacks are not reverted, and `--pin` of the newer tag SHALL contain both deltas when both have landed. This sibling pin collision is a named residual, not a reason to skip the reasoning-effort sanitize. Apply SHALL commit the Guard plugin `agent/request` / `agent/request-error` listeners, `sanitizeReasoningEffort` / `isReasoningEffortRejection` in `dsh_plugin_lib.js`, the spawn gate `dsh_reasoning_effort_spawn` keyed by `parentSession` (child detected from `agent.session.header`, never from LLM `payload.provider`), the dsh-labelled covenant-flow line (after this-class 400 on a child, MUST NOT spawn the same preset; residual `#518` on the root), and goldens in the product first, then `implantar --pin` of that tag on Cripto. `install.sh --pin` SHALL still copy `.dsh/` always. `CLIENT_KEYS` SHALL remain three names. `SCHEMA_MAJOR` SHALL remain 1. Cripto overlay SHALL keep `clients.dsh.auto: false` and record `pin` as that tag. The fourth harness remains a skin, not yaml law. Dual-write of T0–T17 into `.dsh/` remains forbidden. Stubs under `.dsh/skills/` MUST stay at most 8 non-empty body lines. `AGENTS.md` MUST NOT gain a reasoning-effort line. `deepseek-ai/deepseek-harness` MUST NOT be vendored. `process-fsm.yaml` MUST NOT change. Authenticated dump of dsh web `:3080` (Q3=A) SHALL remain the human DoD for one isolated Apply or reviewer spawn and MUST NOT be replaced by pytest goldens.

#### Scenario: Next free patch pin refreshes the dsh reasoning-effort sanitize on Cripto
- **WHEN** overlay is valid and `implantar --pin` of the next unused patch tag Apply confirmed on origin completes on Cripto
- **THEN** `.dsh/plugin/process-fsm-guard.js` in the consumer sanitizes rejected reasoning effort on `agent/request`
- **AND** overlay contains `pin` equal to that confirmed tag
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is the next unused patch (`v1.1.7` when free)
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin

#### Scenario: Pin does not revert sibling #818
- **WHEN** #818 has already landed on the product tip before this card tags
- **THEN** Apply rebases so `dsh_plugin_lib.js` and the Guard plugin keep both haystacks
- **AND** `--pin` of the newer tag contains both deltas

#### Scenario: Human dump remains mandatory
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows one isolated Apply or reviewer spawn entering the turn, running at least one tool, and leaving a closing message with zero this-class rejections on that spawn
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit

### Requirement: Citation-vs-role grill deny ships as product patch pin
This change SHALL ship in product `oalansilva/covenant-flow` as a patch tag (not a schema major). Live overlay/pin-tests are `v1.1.6`. Sibling [#817](https://github.com/oalansilva/crypto/issues/817) (`card-817-dsh-reasoning-effort`) also expects `v1.1.7` and changes the same nucleus (`dsh_plugin_lib.js` and `.dsh/plugin/process-fsm-guard.js`: grill → `dsh_reasoning_effort_spawn` → cordis → `runGuard`, plus `agent/request` / `agent/request-error`). Apply SHALL `gh api repos/oalansilva/covenant-flow/tags` **and** rebase the product on the tag/tip that already exists. Apply MUST NOT pin from base `v1.1.6` after the sibling (that clobbers the sibling sanitizer/gate). The fallback next unused patch covers the **number** only, not rebase/merge. Pin-tests SHALL bump to **this** card's tag after that rebase and MUST NOT hardcode `v1.1.7` in a vacuum. If `v1.1.7` is still free and the tip is still `v1.1.6`, Apply MAY tag `v1.1.7`; if #817 already took it, Apply SHALL use the next unused patch and MUST NOT bump major. `SCHEMA_MAJOR` SHALL remain 1. Apply SHALL commit the updated `isGrillShapedSpawn` helper and goldens in `scripts/process-fsm/test_dsh_grill_spawn.py` on top of the rebased tip, then `implantar --pin` of **this** card's tag on Cripto. Overlay SHALL record `pin` as that tag. `clients.dsh.auto` SHALL remain `false`. `AGENTS.md` MUST NOT gain a line for this rule. The canonical T1 comment text MUST NOT change. Cursor and Grok grill spawn MUST remain allowed. Client skins under `.grok/` `.dsh/` `.opencode/` for `grill-card` MUST stay at most 8 non-empty body lines. Apply MUST NOT revert `dsh_reasoning_effort_spawn` or the `agent/request` listeners.

#### Scenario: Pin materializes the citation-vs-role deny on Cripto
- **WHEN** overlay is valid and `implantar --pin` of this card's tag completes on Cripto
- **THEN** `scripts/process-fsm/dsh_plugin_lib.js` distinguishes grill papel from citation
- **AND** overlay contains `pin:` equal to **this** card's tag after rebase (not a hardcoded `v1.1.7` in a vacuum)
- **AND** `clients.dsh.auto` remains `false`
- **AND** `SCHEMA_MAJOR` remains 1
- **AND** grill-card stubs under `.grok/` `.dsh/` `.opencode/` remain at most 8 non-empty body lines
- **AND** if the rebased tip already contained `dsh_reasoning_effort_spawn` or `agent/request`, those remain after pin

#### Scenario: Product tag is patch not major
- **WHEN** the product repository is tagged for this change
- **THEN** the tag is this card's patch after `gh api` tags and rebase on the existing tip
- **AND** it is not `v2.0.0`
- **AND** `deepseek-ai/deepseek-harness` is still not vendored
- **AND** `process-fsm.yaml` is unchanged by this pin
- **AND** `scripts/process-fsm/guard.py` source still does not contain `grill-card`, `dsh_grill_spawn`, or `isGrillShapedSpawn`

#### Scenario: Pin from v1.1.6 must not clobber sibling #817
- **WHEN** origin already has a tag/tip from #817 on the same nucleus
- **THEN** Apply rebases onto that tag/tip before committing this card's helper
- **AND** Apply MUST NOT `implantar --pin` a tree based on `v1.1.6` that omits `dsh_reasoning_effort_spawn`
- **AND** the next unused patch number MAY be used only after that rebase

