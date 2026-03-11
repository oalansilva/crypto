## Why

The current Kanban mobile experience is still not aligned with the intended product direction. Alan wants a more app-like mobile Kanban with one stage visible at a time, better card readability, stronger touch interactions, and a clearer task-detail experience.

The new direction should rethink the mobile Kanban UI using patterns closer to Trello / Jira / ClickUp while preserving workflow semantics.

## What Changes

- Redesign the mobile Kanban experience around a **single-stage-at-a-time** layout with horizontal stage navigation.
- Add a fixed header, filter bar, stage navigation, card list, and floating primary action tailored for mobile.
- Redesign task cards for touch-friendly reading and interactions.
- Introduce a full-screen bottom-sheet detail view for tasks.
- Define mobile gestures and performance requirements (lazy loading, cache, websocket updates).

## Capabilities

### New Capabilities
- `mobile-kanban-ui`: mobile-first Kanban navigation, cards, detail view, and gestures.

### Modified Capabilities
- `kanban`: mobile interaction model, visual layout, and performance model.

## Impact

- Frontend Kanban page layout and interactions
- Mobile-specific components (header, filters, tabs/swipe, FAB, bottom sheet)
- API/real-time strategy considerations for performance
- Playwright/mobile validation scenarios
