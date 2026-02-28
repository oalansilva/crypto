## ADDED Requirements

### Requirement: Mobile Kanban layout
The system MUST render the `/kanban` experience in a mobile-friendly layout on small screens without changing the desktop layout.

#### Scenario: Mobile layout activates on small screens
- **WHEN** the user opens `/kanban` on a device/screen size below the defined breakpoint
- **THEN** the Kanban UI uses the mobile layout (touch-friendly spacing, readable typography, and mobile navigation patterns)

#### Scenario: Desktop layout remains unchanged
- **WHEN** the user opens `/kanban` on a desktop-sized screen
- **THEN** the Kanban UI matches the existing desktop layout and behavior (no visual/layout regression)

### Requirement: Touch-first interactions
The system MUST provide touch-friendly interactions for core Kanban usage on mobile.

#### Scenario: Tapping a card is reliable
- **WHEN** the user taps a Kanban card on mobile
- **THEN** the system opens the card (or its details/actions) without requiring pixel-precise clicks

#### Scenario: Primary actions are reachable
- **WHEN** the user is on `/kanban` in mobile layout
- **THEN** the primary Kanban actions defined for the MVP are accessible without requiring desktop-only UI affordances

### Requirement: PWA installability (minimum)
The system MUST provide the minimum required configuration for the app to be installable as a PWA and run in standalone mode.

#### Scenario: Manifest is available
- **WHEN** the user loads the app in a modern browser that supports PWAs
- **THEN** a valid web app manifest is served and includes name, icons, and a start_url

#### Scenario: Standalone mode works
- **WHEN** the user installs the PWA and launches it from the home screen
- **THEN** the app opens in standalone mode and `/kanban` is reachable as the primary focus for this MVP
