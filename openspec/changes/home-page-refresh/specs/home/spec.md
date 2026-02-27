## ADDED Requirements

### Requirement: Home is a navigational hub for core workflows
The system MUST present a Home page that helps users quickly access the main workflows of the product.

#### Scenario: User opens Home
- **WHEN** the user navigates to `/`
- **THEN** the system MUST render a Home page with clear entrypoints to the main workflows

### Requirement: Home shows a Quick Actions section
The Home page MUST provide a “Quick Actions” (or equivalent) section with shortcuts to the following destinations:
- Favorites Dashboard
- Monitor
- Combo Strategies
- Strategy Lab
- Arbitrage
- External Balances
- Kanban
- OpenSpec

#### Scenario: User uses a Home shortcut
- **WHEN** the user clicks a shortcut card/button on Home
- **THEN** the system MUST navigate to the corresponding destination page

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
