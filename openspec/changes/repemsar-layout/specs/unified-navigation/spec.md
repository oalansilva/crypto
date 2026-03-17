## ADDED Requirements

### Requirement: Single Navigation Component
The system SHALL use a single navigation component (`AppNav`) that is rendered on ALL pages, eliminating page-specific headers and menus.

#### Scenario: Navigation on all pages
- **WHEN** user visits any page (/, /favorites, /monitor, /kanban, /lab, /arbitrage, /combo/select, /external/balances)
- **THEN** the same navigation component MUST be visible

#### Scenario: No duplicate headers
- **WHEN** page renders
- **THEN** there MUST be exactly ONE header/navigation element visible

---

### Requirement: Desktop Navigation
The system SHALL display a horizontal top navigation bar on desktop (viewport >= 768px) with all menu items visible.

#### Scenario: Desktop nav items
- **WHEN** viewport is desktop (>= 768px)
- **THEN** all navigation links MUST be displayed horizontally in the header

---

### Requirement: Mobile Navigation
The system SHALL display a hamburger menu icon on mobile (viewport < 768px) that opens a slide-out or bottom sheet menu when tapped.

#### Scenario: Mobile hamburger icon
- **WHEN** viewport is mobile (< 768px)
- **THEN** hamburger icon MUST be visible in header

#### Scenario: Mobile menu open
- **WHEN** user taps hamburger icon on mobile
- **THEN** menu MUST slide in from side or appear as bottom sheet

#### Scenario: Mobile menu close
- **WHEN** user taps outside the mobile menu or close button
- **THEN** menu MUST close

---

### Requirement: Active Link Highlighting
The system SHALL highlight the current page link in the navigation.

#### Scenario: Active page indicator
- **WHEN** user is on /monitor page
- **THEN** the "Monitor" link MUST be visually highlighted (different color/background)
