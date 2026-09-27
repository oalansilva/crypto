## ADDED Requirements

### Requirement: Guard allows authorized OpenSpec archive on release-* with resolved package
When `kind` is overlay `design_globs`, session `q` is missing/unreadable, and `q_git` matches `release-*` (not `develop`/`main`, not `card-<id>-*`), the Guard SHALL NOT deny solely because `bound_card` is `⊥`. For every extracted design path in the envelope, the Guard MUST map a card id from the OpenSpec change name: `openspec/changes/<change>/…` or `openspec/changes/archive/<YYYY-MM-DD>-<change>/…` with `<change>` matching `^(card|issue)-(\d+)`. Title-fuzzy mapping MUST NOT authorize the write. The Guard MUST query the injected `status_provider` with that id (MUST NOT use session `bound_card` as the Status key). Allow MUST require Status exactly `Homologado` for every mapped id. If `RELEASE_CARDS` is set, `parse_package_cards` MUST succeed and every mapped id MUST be a member of that list **and** still `Homologado`; the env list alone MUST NOT allow. `RELEASE_CARDS` empty or absent MUST NOT be an allow token; the live `Homologado` Status of the mapped id is the package proof. If any design path is under `frontend/public/prototypes/`, lacks a card id, has unreadable Status, or maps to a non-`Homologado` card, the envelope MUST deny. Deny for unidentified package or unreadable Status MUST use reason `fail_closed`. Deny for a resolved card that is not in the authorized Homologado package MUST use reason `outside_package`. `agent_message`/`reason` MUST name the reason and, when mapped, the card id. Product writes, sidecar mutation, Status `item-edit`, and `card-<id>-*` design allows MUST stay unchanged. Unit tests MUST inject `status_provider` and MUST NOT call GitHub. `.cursor/process-fsm.yaml` MUST NOT gain state, event, hook, or `enabled_tools`.

#### Scenario: Replay fail_closed on release-* without resolved package
- **WHEN** stdin is `Write` of a path under `openspec/changes/` , `q_git` is `release-2026-08-26`, session `status` is omitted, `bound_card` is `⊥`, and the change name has no `card-<id>`/`issue-<id>` prefix
- **THEN** the Guard returns `permission: deny` and `decision: deny`
- **AND** `agent_message` contains `fail_closed`

#### Scenario: Archive of Homologado change is allowed on release-* unbound
- **WHEN** stdin is `Write` of `openspec/changes/card-1017-mapa-juizo-execucao/proposal.md` with `q_git=release-2026-09-22`, session `status` omitted, `bound_card=⊥`, and `status_provider("1017")` returns `Homologado`
- **THEN** the Guard returns `permission: allow` and `decision: allow`
- **AND** `evaluate(write_produto)` is not invoked

#### Scenario: Archive destination path is allowed for the same Homologado card
- **WHEN** stdin is `Write` of `openspec/changes/archive/2026-09-22-card-1017-mapa-juizo-execucao/proposal.md` with `q_git` matching `release-*`, session `status` omitted, and `status_provider("1017")` returns `Homologado`
- **THEN** the Guard returns `permission: allow` and `decision: allow`

#### Scenario: Unreadable Status of the mapped card stays fail_closed
- **WHEN** stdin is `Write` of `openspec/changes/card-1017-x/design.md` on `q_git=release-2026-09-22` with session `status` omitted and `status_provider("1017")` returns nothing
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` contains `fail_closed`

#### Scenario: Mapped card not Homologado is outside_package
- **WHEN** stdin is `Write` of `openspec/changes/card-1017-x/design.md` on `q_git=release-2026-09-22` with session `status` omitted and `status_provider("1017")` returns `Design`
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` contains `outside_package`

#### Scenario: Declared RELEASE_CARDS list alone does not allow
- **WHEN** `RELEASE_CARDS=1017` and stdin is `Write` of `openspec/changes/card-1017-x/design.md` on `q_git=release-2026-09-22` with session `status` omitted and `status_provider("1017")` returns `Todo`
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` contains `outside_package`
- **AND** the env list is not treated as an allow token

#### Scenario: Homologado card absent from RELEASE_CARDS is denied
- **WHEN** `RELEASE_CARDS=999` is valid and stdin is `Write` of `openspec/changes/card-1017-x/design.md` on `q_git=release-2026-09-22` with `status_provider("1017")` returning `Homologado`
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` contains `outside_package`

#### Scenario: Prototype path on release-* unbound stays fail_closed
- **WHEN** stdin is `Write` of `frontend/public/prototypes/x/index.html` with `q_git` matching `release-*` and session `status` omitted
- **THEN** the Guard returns `permission: deny`
- **AND** `agent_message` contains `fail_closed`

#### Scenario: Product write on release-* unbound stays denied
- **WHEN** stdin is `Write` of an overlay `product_globs` path with `q_git` matching `release-*` and session `status` omitted
- **THEN** the Guard returns `permission: deny`
- **AND** it MUST NOT take the archive exception

#### Scenario: Mixed prototype and archive envelope is denied
- **WHEN** stdin extracts both `openspec/changes/card-1017-x/proposal.md` and `frontend/public/prototypes/x/index.html` on `q_git` matching `release-*` with `status_provider("1017")` returning `Homologado`
- **THEN** the Guard returns `permission: deny`

#### Scenario: Fixtures inject status_provider without GitHub
- **WHEN** pytest exercises the archive exception
- **THEN** `status_provider` is injected with the mapped card id
- **AND** no network call to GitHub is made

## MODIFIED Requirements

### Requirement: Fail-closed is asymmetric
If `status`/`q` is missing, unreadable, or a Status provider times out, the Guard MUST deny overlay `product_globs` writes and MUST allow writes whose path matches overlay `design_globs` when the path worktree branch already matches `card-<id>-*`. Design writes on `q_git=develop` or `q_git=main` with unreadable session `q` MUST remain deny (`fail_closed`); the release-* archive exception MUST NOT apply to those branches. If `.covenant-flow/overlay.yaml` is missing or invalid, the Guard MUST deny product writes (fail-closed) and MUST NOT treat missing overlay as allow. Unit tests MUST inject `status` in the stdin JSON and MUST NOT call GitHub.

#### Scenario: Status unreadable, product path
- **WHEN** stdin omits `status` and the Status provider returns nothing, and the path matches overlay `product_globs`
- **THEN** permission is `deny`

#### Scenario: Status unreadable, design path on card branch
- **WHEN** stdin omits `status` and the path is under `openspec/changes/` or `frontend/public/prototypes/` and `q_git` matches `card-<id>-*`
- **THEN** permission is `allow`

#### Scenario: Status unreadable, design path on develop
- **WHEN** stdin omits `status` and the path is under `openspec/changes/` and `q_git` is `develop`
- **THEN** permission is `deny`
- **AND** `agent_message` contains `fail_closed`
- **AND** the release-* archive exception MUST NOT apply

#### Scenario: Fixtures without GitHub
- **WHEN** `pytest scripts/process-fsm -q` runs
- **THEN** Guard fixtures execute from stdin-like JSON using injected `status` and fake worktrees or stubs
- **AND** no network call to GitHub is made

#### Scenario: Missing overlay denies product writes
- **WHEN** overlay is absent or fails schema and stdin is a product-path `Write`
- **THEN** permission is `deny`
- **AND** missing overlay is not an allow token
