## ADDED Requirements

### Requirement: Canonical prototype file is index.html
T5 SHALL measure clone landmarks and `copied` against the canonical prototype file only: `frontend/public/prototypes/<q_git>/index.html`. It MUST NOT concatenate every `*.html` in that directory. A sibling clone (for example `landing.html`) MUST NOT satisfy landmarks or `copied` for the directory index. If `index.html` is missing and the directory contains exactly one `*.html`, T5 SHALL read that single file. If `index.html` is missing and the directory contains zero or two or more `*.html` files, the measured HTML is empty and the gate MUST refuse. Extra clone URLs for additional existing surfaces MAY be published on the card comment; T5 still measures only the canonical index. Apply MUST implement this as `canonical_proto_html` replacing `concatenate_proto_html`.

#### Scenario: Panel index plus sibling landing clone is refused
- **WHEN** `design.md` declares `live_route: landing` or `surface: existing` and the prototype directory contains a BEFORE/AFTER panel `index.html` (no landing h1/FAQ/CTA, `copied` 0) plus a sibling `landing.html` that is a v4 clone with catalog landmarks and `copied` > 0
- **THEN** the clone gate returns false
- **AND** concatenating all `*.html` in the folder MUST NOT be used to pass

#### Scenario: Single html fallback when index is missing
- **WHEN** the prototype directory has exactly one `*.html` file and no `index.html`
- **THEN** T5 reads that file as the canonical HTML

#### Scenario: Two html files and no index refuse
- **WHEN** the prototype directory has two or more `*.html` files and no `index.html`
- **THEN** the measured HTML is empty
- **AND** the clone gate returns false for an existing-surface declaration

### Requirement: Public landing catalog key is not an authenticated route
The HEAD catalog SHALL include a sibling key `landing` with `kind: public` so public HTML is not treated as an authenticated app route. Keys that start with `/` default to `kind: authenticated` when `kind` is omitted. `routes_from_catalog` SHALL include keys that start with `/` **or** have `kind: public`. `LIVE_ROUTE_RE` SHALL capture `(\/\S+|landing|N/A)`. Declaring `live_route: landing` without that key in HEAD MUST refuse. This harness change SHALL seed the `landing` entry; a product Design MUST NOT add the key in the same change to bypass the gate.

#### Scenario: Seeded landing landmarks
- **WHEN** the catalog is read after Apply of this change
- **THEN** key `landing` has `kind: public`, selectors `.faq-section` and `.button-primary`, and texts including `Comprar ou vender cripto? O Cripto Farol responde.`, `FAQ`, and `Quero meus 6 meses grátis`
- **AND** `/monitor` remains an authenticated catalog key (not `kind: public`)

#### Scenario: Landing declared without HEAD key refuses
- **WHEN** `live_route` is `landing` and HEAD catalog has no `landing` key
- **THEN** T5 refuses
- **AND** adding `landing` only in the worktree catalog does not pass the gate

#### Scenario: V4 clone as index passes landing and not because of path 790
- **WHEN** the canonical `index.html` is a clone of `frontend/public/prototypes/cripto-farol-landing-v4/` with landing landmarks and `copied` > 0, stored as a test fixture (not `frontend/public/prototypes/card-790-copy-spot/`)
- **THEN** `classify` against `landing` is PASS
- **AND** the result MUST NOT depend on the file path containing `790`

### Requirement: UI none skip is narrowed to harness without existing surface
`evaluate_clone_gate` MUST NOT return true solely because `UI impact: none`. UI none SHALL skip catalog/`copied` only when the design does **not** require an existing clone (`live_route` is not a `/` path, is not `landing`, and `surface` is not `existing`) — including this harness card with `live_route: N/A`, `surface: new`, and no prototype directory. When `surface: existing` or `live_route` is a catalog key (`/` or `landing`), T5 SHALL require a prototype and SHALL measure the canonical index even if `UI impact: none`. Missing proto in that case MUST refuse. Evasion that lies `UI impact: none` / `surface: new` on visible copy of an existing page is out of machine scope (skill/A/B); the machine still refuses Prototype N/A when existing/catalog is declared.

#### Scenario: UI none harness without proto still passes
- **WHEN** `design.md` declares `UI impact: none`, `live_route: N/A` with a non-empty justification, and `surface: new`, the change directory has the three Markdown files plus a spec, and no prototype HTML exists
- **THEN** `files_g_design` is true
- **AND** T5 does not require catalog landmarks or `copied`

#### Scenario: Existing surface without proto is refused even if UI none
- **WHEN** `design.md` declares `surface: existing` or `live_route: landing` (or another catalog key) and no prototype HTML exists
- **THEN** `files_g_design` is false
- **AND** `UI impact: none` does not skip the gate

## MODIFIED Requirements

### Requirement: G_design composes OpenSpec files and the clone gate
`files_g_design` SHALL return true only when `openspec/changes/<q_git>/` contains `proposal.md`, `design.md`, `tasks.md`, and at least one `specs/**/*.md`, **and** the clone gate defined by this capability passes. `G_design` on T5 (`submeter_design`) SHALL use that composed predicate when `g_design` is not injected. Injected `g_design=True` in unit tests MAY bypass measurement; live `process_event` MUST measure.

#### Scenario: UI none with OpenSpec files passes
- **WHEN** `design.md` declares `UI impact: none` with `live_route: N/A` justified and `surface: new` (or no existing-surface declaration), the change directory has the three Markdown files plus a spec, and no existing-surface prototype is required
- **THEN** `files_g_design` is true
- **AND** T5 does not require catalog landmarks or `copied`

#### Scenario: Affected existing proto without parseable field is refused
- **WHEN** `design.md` declares `UI impact: affected`, a prototype HTML exists under `frontend/public/prototypes/<q_git>/`, and neither `live_route:` nor `surface:` is present
- **THEN** `files_g_design` is false
- **AND** T5 rejects with `guard:G_design`

### Requirement: Parseable live_route and surface fields
`design.md` SHALL declare machine-parseable lines `live_route:` and/or `surface: existing|new`. `surface: existing` or a `live_route:` that is a catalog key (starts with `/` **or** is `landing`) SHALL require a HEAD catalog key, landmarks on the canonical `index.html`, and `copied` > 0. `surface: new` or `live_route: N/A` with a non-empty justification SHALL skip catalog and `copied` checks **unless** `live_route` is a catalog key. Missing fields on an affected prototype MUST NOT be treated as a new surface.

#### Scenario: Existing monitor route requires catalog
- **WHEN** `design.md` contains `live_route: /monitor` or `surface: existing` and a prototype HTML exists
- **THEN** T5 looks up `/monitor` in the HEAD catalog
- **AND** it refuses if the key is missing, landmarks fail, or `copied` is 0

#### Scenario: New surface skips catalog
- **WHEN** `design.md` contains `surface: new` or `live_route: N/A` plus a non-empty justification and a prototype HTML exists, and `live_route` is not a catalog key
- **THEN** the catalog and `copied` checks do not run
- **AND** T5 still requires the three Markdown files plus specs

### Requirement: Versioned landmark catalog is fail-closed
The repository SHALL contain `scripts/process-fsm/route-landmarks.yaml` (`version: 1`) keyed by live route path and by public HTML keys with `kind: public`. This change SHALL seed `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`, and `landing`. Lookup SHALL use the catalog at HEAD (`git show HEAD:scripts/process-fsm/route-landmarks.yaml` when that path exists in HEAD). A key added only in the working tree of the same product Design change MUST NOT satisfy the gate.

#### Scenario: Declared route missing from HEAD catalog
- **WHEN** `live_route` is `/profile` and HEAD catalog has no `/profile` key
- **THEN** T5 refuses
- **AND** adding `/profile` only in the worktree catalog does not pass the gate

#### Scenario: Seeded monitor landmarks
- **WHEN** the catalog is read after Apply of this change
- **THEN** `/monitor` lists selector `table.signals` and texts including `Status`, `Preço`, `Risco até stop`, and `Operar`

### Requirement: Static HTML read measures landmarks and copied bytes
T5 SHALL read the canonical prototype HTML from disk under `frontend/public/prototypes/<q_git>/index.html` (or the documented single-file fallback) with no network and no authenticated Playwright. Every catalog `selectors[]` and `texts[]` for the declared route MUST appear as a substring in that canonical HTML. `copied` SHALL be the UTF-8 byte sum of intervals between paired `COPIED:start` and `COPIED:end` markers in that same file. Missing markers or sum 0 MUST refuse.

#### Scenario: Copied markers missing
- **WHEN** the canonical prototype HTML has catalog landmarks but no `COPIED:start`/`COPIED:end` pair
- **THEN** T5 refuses

#### Scenario: Copied sum is zero
- **WHEN** the canonical prototype HTML has empty `COPIED:start`…`COPIED:end` intervals whose UTF-8 sum is 0
- **THEN** T5 refuses

#### Scenario: Landmarks present and copied positive
- **WHEN** the canonical prototype HTML contains every catalog selector and text for `/monitor` and the `copied` sum is greater than 0
- **THEN** the clone gate returns true for that existing route
