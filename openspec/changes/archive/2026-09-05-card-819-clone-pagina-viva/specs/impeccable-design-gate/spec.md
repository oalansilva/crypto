## ADDED Requirements

### Requirement: Existing surface includes public HTML not only authenticated routes
An existing product surface SHALL include an authenticated catalog route **and** public HTML that is in the landmark catalog (`landing` = landing v4 at `https://criptofarol.com.br/`, source `frontend/public/prototypes/cripto-farol-landing-v4/`). Design, critics, and T5 MUST treat that public page as clone-required when `live_route: landing` or `surface: existing` targets it. Cloning only authenticated `/monitor`-style chrome is not sufficient for landing copy. A BEFORE/AFTER panel MUST be P0 as the canonical prototype URL even when a clone exists as a sibling file in the same folder.

#### Scenario: Landing copy proto is the live page plus delta
- **WHEN** a card changes visible copy on the public landing
- **THEN** the canonical prototype URL (`…/prototypes/<slug>/` serving `index.html`) contains the catalog landing landmarks (h1 «Comprar ou vender cripto? O Cripto Farol responde.», FAQ, CTA «Quero meus 6 meses grátis») plus only the card delta
- **AND** a panel titled as copy ANTES/DEPOIS MUST NOT be that canonical URL

#### Scenario: Sibling clone does not redeem a panel index
- **WHEN** `index.html` is a BEFORE/AFTER panel and `landing.html` in the same directory is a v4 clone
- **THEN** Assessment MUST record P0
- **AND** T5 MUST refuse against `landing` because it measures `index.html` only

### Requirement: Visible copy cannot use Prototype N/A
Visible copy on an existing page (landing / Ajuda / Perfil) SHALL be treated as the page having changed. Design MUST NOT record `Prototype: N/A` for that case. T5 SHALL refuse when `surface: existing` or `live_route` is a catalog key and no prototype HTML exists. Lying `UI impact: none` / `surface: new` on visible copy of an existing page is a skill/A/B finding; the machine still refuses Prototype N/A when existing/catalog is declared.

#### Scenario: Copy-only existing surface without proto is blocked
- **WHEN** `design.md` declares an existing surface or a catalog `live_route` and Prototype is N/A or the proto directory has no HTML
- **THEN** the Design MUST NOT reach approval via T5
- **AND** `UI impact: none` does not skip the clone gate

### Requirement: N existing surfaces use a primary clone URL plus extras
When a card touches N existing surfaces with visible copy, the canonical prototype URL SHALL be the cloned primary page (`index.html`). Additional cloned pages SHALL have extra URLs listed on the card comment (not a panel of N states on the index). T5 SHALL still measure only the canonical index.

#### Scenario: Multi-surface card does not panel the index
- **WHEN** a card changes landing plus Ajuda plus Perfil
- **THEN** the primary URL is the cloned primary page
- **AND** the other visible-copy pages are extra clone URLs
- **AND** the index MUST NOT be a gallery or BEFORE/AFTER panel of the N surfaces

## MODIFIED Requirements

### Requirement: Prototype clone+delta without HTML dump
For an existing product surface, the prototype MUST clone the live page — authenticated route listing/headers/actions/expand **or** catalogued public HTML (landing v4) — plus shell/nav/tokens/density where that chrome exists, and apply only the card delta. Cloning only the current shell/nav/tokens/density is not sufficient. A BEFORE/AFTER panel or “N estados” gallery MUST NOT be the canonical URL even if a clone sibling exists. Design, critics, and operator chat MUST use the navigable URL, screenshot, and digest — they MUST NOT dump prototype HTML into chat or `design.md`. `/opsx:apply` MUST still read the prototype file on disk as the layout spec. Polish MUST patch the prototype file; it MUST NOT rewrite the whole HTML in the LLM. New surfaces still compose from the token sheet plus the authenticated app shell, not a generic landing; new surfaces are exempt from catalog/`copied` when `surface: new` or `live_route: N/A` is declared and `live_route` is not a catalog key.

#### Scenario: Critics review URL and digest
- **WHEN** Assessment A or B reviews a UI-affected prototype
- **THEN** the spawn context includes the HTTP URL, screenshot, and digest
- **AND** it does not include the prototype HTML source as chat payload

#### Scenario: Apply still reads the prototype file
- **WHEN** `/opsx:apply` implements a UI-affected card
- **THEN** it reads `frontend/public/prototypes/<change-or-card-slug>/` from disk as the layout spec
- **AND** it does not treat `design.md` bullets as a replacement for that file

#### Scenario: Polish is a patch
- **WHEN** targeted Impeccable fixes land on the prototype
- **THEN** the edit is a patch to the existing file
- **AND** the LLM MUST NOT emit a full-file HTML rewrite as the polish step

#### Scenario: Existing route clone includes listing landmarks
- **WHEN** Design clones an existing product surface such as `/monitor`
- **THEN** the prototype HTML contains the catalog landmarks for that route
- **AND** sidebar 224px plus `--bg-*` tokens alone MUST NOT pass fidelity

### Requirement: Existing-route prototype MUST clone live-route landmarks
For `UI impact: affected` when the surface already exists, the prototype MUST clone the live page (authenticated catalog route **or** public HTML key `landing`) and apply only the card delta inside that topology. Shell width 224px, `--bg-*` tokens, and the token sheet MUST NOT be treated as sufficient fidelity. Blocking fidelity is the versioned landmark catalog for that key. The canonical URL is the directory index (`index.html`), not a linked sibling.

#### Scenario: Monitor proto without listing landmarks is P0
- **WHEN** Assessment A or B reviews a `/monitor` prototype that has sidebar 224px and correct tokens but lacks `table.signals` or headers `Status` / `Preço` / `Risco até stop` / `Operar`
- **THEN** the verdict MUST be `BLOCKED` with a P0 fidelity finding
- **AND** chrome-only PASS is forbidden

#### Scenario: Delta stays inside the live topology
- **WHEN** a card changes a detail on an existing route
- **THEN** the prototype URL shows the same listing/actions landmarks as the live route
- **AND** the card delta is inside that topology, not a parallel layout

### Requirement: Gallery of states is P0 on list-plus-detail routes
When the live product is list-plus-detail, a prototype that renders N states as N cards in a grid MUST be a P0. Named anti-pattern: “N estados ⇒ N cards numa grelha”. A BEFORE/AFTER panel as the canonical `index.html` is the same class of P0 for any existing surface, including public landing, even when a clone sibling file exists. This SHALL NOT treat a live template grid (Combo `/combo/select`) as that anti-pattern when the catalog landmarks for that route are present.

#### Scenario: Four-card gallery for Monitor is P0
- **WHEN** a `/monitor` prototype is a 2×2 gallery of state cards instead of `table.signals` plus row expand
- **THEN** Assessment MUST record P0
- **AND** T5 clone gate MUST classify that HTML as BLOCKED against `/monitor`

#### Scenario: Landing BEFORE/AFTER panel is P0
- **WHEN** the canonical prototype URL for landing copy is a panel of ANTES/DEPOIS blocks (including a link to `./landing.html`) instead of the cloned v4 page
- **THEN** Assessment MUST record P0
- **AND** T5 MUST refuse against catalog key `landing`
