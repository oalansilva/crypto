# mobile-kanban-ui Specification

## Purpose
Mobile Kanban UI requirements were discontinued when the internal `/kanban` board was removed. Operational board work happens on GitHub Project 1.

## Requirements
### Requirement: Mobile Kanban UI is not exposed in the product
The authenticated product MUST NOT render a mobile Kanban board UI. Operational card work MUST happen on GitHub Project 1 instead of an internal `/kanban` route.

#### Scenario: Mobile user has no internal kanban surface
- **WHEN** a user opens the app on a mobile viewport
- **THEN** the product MUST NOT expose a mobile Kanban stage view, swipe navigation, or bottom-sheet task detail for an internal board
