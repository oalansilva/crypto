## ADDED Requirements

### Requirement: Favorites screen is mobile-first and responsive
The system MUST provide a mobile-friendly experience for the Favorites screen (`/favorites`) without reducing desktop usability.

#### Scenario: Small viewport uses a stacked layout
- **WHEN** the viewport width is below the mobile breakpoint
- **THEN** favorites are presented in a stacked/card layout (no horizontal scrolling required)

#### Scenario: Desktop viewport keeps the desktop layout
- **WHEN** the viewport width is at or above the desktop breakpoint
- **THEN** the Favorites screen preserves the existing desktop layout and information density

### Requirement: Mobile actions are touch-friendly
On mobile, the system MUST make primary actions easy to access and safe to use.

#### Scenario: Touch targets meet minimum size
- **WHEN** the Favorites screen is rendered on a mobile viewport
- **THEN** primary action controls (e.g., edit notes, change tier, delete) have touch targets of at least 44x44px (or equivalent)

#### Scenario: Destructive actions require confirmation
- **WHEN** the user triggers a destructive action (e.g., delete a favorite)
- **THEN** the UI requires an explicit confirmation before the action is executed

### Requirement: Key fields remain readable on mobile
The system MUST prioritize readability for the most important fields on small screens.

#### Scenario: The primary summary is visible without expanding
- **WHEN** a favorite is shown on a mobile viewport
- **THEN** the card shows at minimum: symbol, strategy/template name, tier (or “No tier”), and current status (e.g., HOLD vs waiting)

#### Scenario: Secondary details are collapsible
- **WHEN** a favorite has additional details (e.g., notes, parameters, metrics)
- **THEN** the UI presents them in a collapsible section to minimize scrolling
