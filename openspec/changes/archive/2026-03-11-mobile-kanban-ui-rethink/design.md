## Context

Alan provided a detailed briefing for a new mobile Kanban interface. The desired experience is no longer a simple responsive adaptation of desktop columns; it is a mobile-first interaction model.

The new model is based on:
- one stage visible at a time
- swipe + horizontal tabs for stage navigation
- fixed header and fixed filter bar
- scrollable card list for the current stage
- large, touch-friendly cards
- floating action button
- full-screen task detail bottom sheet
- performance protections for mobile

## Goals / Non-Goals

**Goals**
- Make Kanban feel natural on mobile devices.
- Avoid showing all columns at once on narrow screens.
- Improve task scanning, filtering, and task detail access.
- Keep the experience lightweight and performant.

**Non-Goals**
- Rebuilding the desktop Kanban layout in this change.
- Changing business workflow rules.
- Implementing every advanced desktop interaction on mobile.

## Proposed UX Structure

### 1. Screen structure
Mobile screen is divided into:
1. Fixed header
2. Fixed filter bar
3. Stage navigation (swipe + tabs)
4. Card list for the active stage
5. Floating action button

### 2. Stage navigation
- Only **one workflow stage** is visible at a time on mobile.
- Users can switch stage by:
  - horizontal swipe
  - horizontally scrollable stage tabs
- Active tab should show:
  - highlighted state
  - underline
  - badge with item count

### 3. Header
Fixed height ~56px.

Proposed controls:
- menu button
- current project / board label
- search
- notifications

Menu drawer should expose:
- boards
- projects
- settings
- backlog
- users

### 4. Filter bar
Fixed below header (~48px).
Should expose entry points for:
- filters
- type
- assignee
- priority
- labels

Detailed filter options should open in a bottom sheet.

### 5. Card model
Cards should be redesigned with:
- priority stripe
- task type badge (`BUG`, `STORY`, `TASK`, `SPIKE`)
- title (max two lines)
- labels
- status indicators (`comments`, `checklist`, `attachments`, `due`)
- avatars (max 3 visible + overflow count)

### 6. Card interaction
- tap → open detail
- long press → drag mode
- horizontal drag → move to another stage

### 7. Detail view
Task detail should open as a **full-screen bottom sheet** with:
- title
- type + priority
- assignees
- labels
- description
- checklist
- comments
- history
- fixed comment input

### 8. Performance
Minimum expectations:
- lazy load cards
- pagination/batching (e.g. 20 items at a time)
- local cache
- websocket-ready update model

## Review Notes
This change is driven directly by Alan's mobile briefing and should be treated as a product-level UI rethink for Kanban mobile.
