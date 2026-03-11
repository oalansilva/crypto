# mobile-kanban-ui Specification

## Purpose
TBD - created by archiving change mobile-kanban-ui-rethink. Update Purpose after archive.
## Requirements
### Requirement: Mobile Kanban MUST show one stage at a time
The system MUST present only one Kanban stage at a time on mobile viewports.

#### Scenario: Single-stage mobile view
- **WHEN** the user opens Kanban on a mobile viewport
- **THEN** the UI MUST show only one workflow stage at a time
- **AND** the user MUST be able to switch stages horizontally

### Requirement: Mobile Kanban MUST support swipe and tab stage navigation
The system MUST support stage switching through both gestures and tabs.

#### Scenario: Swipe navigation
- **WHEN** the user swipes horizontally on the stage area
- **THEN** the active stage MUST change accordingly

#### Scenario: Tab navigation
- **WHEN** the user taps a stage tab
- **THEN** the corresponding stage MUST become active
- **AND** the active tab MUST remain visually highlighted with count badge

### Requirement: Mobile Kanban MUST provide a touch-friendly card layout
The system MUST render cards in a format optimized for touch and quick reading.

#### Scenario: Card structure
- **WHEN** a card is rendered on mobile
- **THEN** it MUST show priority, type, title, labels, indicators, and assignees in a touch-friendly format

### Requirement: Task detail MUST open as a full-screen bottom sheet
The system MUST open task details in a mobile-appropriate detail surface.

#### Scenario: Open detail
- **WHEN** the user taps a task card
- **THEN** task detail MUST open as a full-screen bottom sheet

### Requirement: Mobile Kanban MUST define performance protections
The system MUST protect mobile usability under larger data volumes.

#### Scenario: Batched loading
- **WHEN** the active stage contains many items
- **THEN** the UI MUST load cards in batches/lazy mode rather than rendering all at once

