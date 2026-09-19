# home Specification

## Purpose
TBD - created by archiving change home-page-refresh. Update Purpose after archive.
## Requirements
### Requirement: Home is a navigational hub for core workflows
The system MUST present a Home page that helps users quickly access the main workflows of the product.

#### Scenario: User opens Home
- **WHEN** the user navigates to `/`
- **THEN** the system MUST render a Home page with clear entrypoints to the main workflows

### Requirement: Home shows a Quick Actions section
The Home page MUST provide shortcuts only to workflows that remain supported by the product and MUST stop exposing Strategy Lab as a destination.

#### Scenario: User uses a Home shortcut
- **WHEN** the user clicks a shortcut card/button on Home
- **THEN** the system MUST navigate only to still-supported destinations
- **AND** no shortcut to Strategy Lab is rendered

### Requirement: Home provides basic product orientation
The Home page MUST include short, non-technical copy that explains what the app is for and suggests a simple starting path.

#### Scenario: User reads “Where to start”
- **WHEN** the user views the top portion of Home
- **THEN** the system MUST show a brief description of the app purpose and a suggested next step (e.g., “Start by adding Favorites, then open Monitor”)

### Requirement: Home content is compact and responsive
The Home layout MUST remain readable and usable on desktop and mobile.

#### Scenario: Mobile layout
- **WHEN** Home is viewed on a narrow viewport
- **THEN** Quick Actions MUST reflow into a vertical/grid layout without truncating the ability to identify and click each destination

### Requirement: Home favorites KPI distinguishes load error from empty catalog

The Início KPI that reads the favorites list SHALL keep error and empty as separate copies. This card does not redesign Home layout, KPIs, or flow.

#### Scenario: Favorites fetch fails on Home

- **WHEN** the Home favorites query errors
- **THEN** the KPI shows «não disponível» and «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

#### Scenario: Home has no favorite after a successful fetch

- **WHEN** the Home favorites query succeeds
- **AND** there is no favorite to feature
- **THEN** the KPI MAY show «Nenhuma estratégia favoritada»

### Requirement: Home KPI does not show a false favorites load error during renewal

On Início (`/home`), during access renewal, the favorites KPI SHALL show the featured strategy when the catalog is on the server. The KPI MUST NOT show «Não foi possível carregar `/api/favorites`.» in that window. A real favorites fetch failure outside renewal continues the existing error copy. This card SHALL NOT redesign Home layout, KPIs, or flow.

#### Scenario: Renewal window shows the featured strategy

- **WHEN** the operator opens `/home`
- **AND** crypto favorites are stored
- **AND** access is being renewed
- **THEN** the «Melhor estratégia (7d)» KPI shows the strategy
- **AND** MUST NOT show «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

#### Scenario: Real Home favorites failure keeps the existing error copy

- **WHEN** the Home favorites query fails by real network error or invalid body
- **AND** the session is not dead
- **THEN** the KPI shows «não disponível» and «Não foi possível carregar `/api/favorites`.»
- **AND** MUST NOT show «Nenhuma estratégia favoritada»

