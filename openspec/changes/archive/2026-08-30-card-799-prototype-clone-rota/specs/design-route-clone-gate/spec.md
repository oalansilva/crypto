## ADDED Requirements

### Requirement: G_design composes OpenSpec files and the clone gate
`files_g_design` SHALL return true only when `openspec/changes/<q_git>/` contains `proposal.md`, `design.md`, `tasks.md`, and at least one `specs/**/*.md`, **and** the clone gate defined by this capability passes. `G_design` on T5 (`submeter_design`) SHALL use that composed predicate when `g_design` is not injected. Injected `g_design=True` in unit tests MAY bypass measurement; live `process_event` MUST measure.

#### Scenario: UI none with OpenSpec files passes
- **WHEN** `design.md` declares `UI impact: none` and the change directory has the three Markdown files plus a spec
- **THEN** `files_g_design` is true
- **AND** T5 does not require catalog landmarks or `copied`

#### Scenario: Affected existing proto without parseable field is refused
- **WHEN** `design.md` declares `UI impact: affected`, a prototype HTML exists under `frontend/public/prototypes/<q_git>/`, and neither `live_route:` nor `surface:` is present
- **THEN** `files_g_design` is false
- **AND** T5 rejects with `guard:G_design`

### Requirement: Parseable live_route and surface fields
`design.md` SHALL declare machine-parseable lines `live_route:` and/or `surface: existing|new`. `surface: existing` or a `live_route:` that starts with `/` SHALL require a HEAD catalog key, landmarks, and `copied` > 0. `surface: new` or `live_route: N/A` with a non-empty justification SHALL skip catalog and `copied` checks. Missing fields on an affected prototype MUST NOT be treated as a new surface.

#### Scenario: Existing monitor route requires catalog
- **WHEN** `design.md` contains `live_route: /monitor` or `surface: existing` and a prototype HTML exists
- **THEN** T5 looks up `/monitor` in the HEAD catalog
- **AND** it refuses if the key is missing, landmarks fail, or `copied` is 0

#### Scenario: New surface skips catalog
- **WHEN** `design.md` contains `surface: new` or `live_route: N/A` plus a non-empty justification and a prototype HTML exists
- **THEN** the catalog and `copied` checks do not run
- **AND** T5 still requires the three Markdown files plus specs

### Requirement: Versioned landmark catalog is fail-closed
The repository SHALL contain `scripts/process-fsm/route-landmarks.yaml` (`version: 1`) keyed by live route path. This change SHALL seed `/monitor`, `/favorites`, `/combo/discovery`, and `/combo/select`. Lookup SHALL use the catalog at HEAD (`git show HEAD:scripts/process-fsm/route-landmarks.yaml` when that path exists in HEAD). A key added only in the working tree of the same product Design change MUST NOT satisfy the gate.

#### Scenario: Declared route missing from HEAD catalog
- **WHEN** `live_route` is `/profile` and HEAD catalog has no `/profile` key
- **THEN** T5 refuses
- **AND** adding `/profile` only in the worktree catalog does not pass the gate

#### Scenario: Seeded monitor landmarks
- **WHEN** the catalog is read after Apply of this change
- **THEN** `/monitor` lists selector `table.signals` and texts including `Status`, `Preço`, `Risco até stop`, and `Operar`

### Requirement: Static HTML read measures landmarks and copied bytes
T5 SHALL read prototype HTML from disk under `frontend/public/prototypes/<q_git>/` with no network and no authenticated Playwright. Every catalog `selectors[]` and `texts[]` for the declared route MUST appear as a substring in the concatenated HTML. `copied` SHALL be the UTF-8 byte sum of intervals between paired `COPIED:start` and `COPIED:end` markers. Missing markers or sum 0 MUST refuse.

#### Scenario: Copied markers missing
- **WHEN** the prototype HTML has catalog landmarks but no `COPIED:start`/`COPIED:end` pair
- **THEN** T5 refuses

#### Scenario: Copied sum is zero
- **WHEN** the prototype HTML has empty `COPIED:start`…`COPIED:end` intervals whose UTF-8 sum is 0
- **THEN** T5 refuses

#### Scenario: Landmarks present and copied positive
- **WHEN** the prototype HTML contains every catalog selector and text for `/monitor` and the `copied` sum is greater than 0
- **THEN** the clone gate returns true for that existing route

### Requirement: Gallery r1 fixture is BLOCKED
The gate SHALL classify the #792 r1 gallery HTML (sha256 `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7`, 21275 bytes, no `table.signals`) as BLOCKED when checked against `/monitor`. Apply MUST store those exact bytes at `scripts/process-fsm/fixtures/792-r1-gallery.html`. Apply MUST NOT patch `frontend/public/prototypes/card-792-monitor-risco-explicito/` or treat the live r2 digest `1a1ff265…` as that fixture.

#### Scenario: r1 gallery bytes fail the monitor catalog
- **WHEN** the static check runs on `scripts/process-fsm/fixtures/792-r1-gallery.html` with `live_route: /monitor`
- **THEN** the result is BLOCKED
- **AND** the file sha256 is `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7`
- **AND** the live #792 r2 prototype path is not overwritten
