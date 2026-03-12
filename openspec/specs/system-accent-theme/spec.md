# system-accent-theme Specification

## Purpose
Define a single, consistent **system accent color** used across the application UI (links, primary actions, focus states, and selected states).

## Requirements

### Requirement: The application exposes a single semantic accent style
The UI MUST use a semantic accent style (token/utility) rather than scattering raw color classes.

#### Scenario: New UI elements use the accent token
- **WHEN** a new interactive element is added (button/link/tab)
- **THEN** it uses the semantic accent token/style
- **AND** it does not introduce hard-coded emerald/green accent classes

### Requirement: The system accent color is blue
The application MUST render the accent color as a blue palette.

#### Scenario: Links render in blue
- **WHEN** a user views any page containing links
- **THEN** link text uses the blue accent palette
- **AND** hover state remains blue and readable on dark backgrounds

#### Scenario: Primary actions render in blue
- **WHEN** a user views primary call-to-action buttons
- **THEN** their accent border/background/hover states use the blue accent palette

#### Scenario: Focus ring renders in blue
- **WHEN** a user focuses an input/button via keyboard
- **THEN** the focus outline/ring uses the blue accent palette

### Requirement: No mixed green/emerald accent remains
The application MUST NOT ship with mixed accent colors in primary UI surfaces.

#### Scenario: Repo-level search guardrail
- **WHEN** the codebase is searched for `text-emerald-`, `border-emerald-`, `bg-emerald-` (and similar green accent patterns)
- **THEN** there are no remaining matches in active UI code
- **OR** matches are explicitly documented as exceptions
