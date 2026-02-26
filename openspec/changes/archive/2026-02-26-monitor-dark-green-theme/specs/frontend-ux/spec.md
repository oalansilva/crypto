## ADDED Requirements

### Requirement: Monitor uses dark-green palette
The UI MUST apply a dark-green palette to the Monitor screen (`/monitor`).

#### Scenario: Background is dark-green (not black)
- **WHEN** the user opens Monitor
- **THEN** the primary background is dark-green (not pure black)

#### Scenario: Readability is preserved
- **WHEN** the theme is applied
- **THEN** text, icons, and controls remain readable on mobile and desktop

#### Scenario: Theme applies to key components
- **WHEN** the theme is applied
- **THEN** it affects at least: filter bar, cards, chart container, and primary buttons
