## ADDED Requirements

### Requirement: Monitor renders responsive mobile cards
The Monitor page SHALL render opportunities in a mobile-usable card layout on narrow viewports instead of relying on the desktop table layout.

#### Scenario: User opens Monitor on a phone viewport
- **WHEN** the user opens `/monitor` on a narrow viewport
- **THEN** opportunities SHALL be visible as stacked cards
- **AND** the desktop signals table SHALL NOT be the primary visible layout
- **AND** the page SHALL NOT require horizontal scrolling to read the core opportunity content

#### Scenario: Mobile cards keep Monitor controls usable
- **WHEN** the user views a Monitor opportunity on a narrow viewport
- **THEN** timeframe controls, management actions, notes, and chart entry actions SHALL remain reachable
- **AND** the detail sections SHALL wrap into a single-column layout that fits the viewport width
