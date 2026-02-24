## ADDED Requirements

### Requirement: Favorites route supports responsive navigation and layout
The UI MUST provide a responsive layout for the Favorites route (`/favorites`) optimized for mobile use.

#### Scenario: Navigation remains accessible on mobile
- **WHEN** the user opens the Favorites screen on a mobile viewport
- **THEN** navigation to other primary screens remains accessible (e.g., via a compact header, drawer, or bottom navigation)

#### Scenario: Filters and search are usable on mobile
- **WHEN** the user uses filters/search on a mobile viewport
- **THEN** the controls are reachable without precision tapping and do not require horizontal scrolling

### Requirement: Favorites screen avoids horizontal scrolling on mobile
The UI MUST avoid horizontal scrolling for the main Favorites content on mobile.

#### Scenario: Content fits within viewport
- **WHEN** the viewport is below the mobile breakpoint
- **THEN** the Favorites list/cards fit within the viewport width and wrap/truncate long text appropriately
