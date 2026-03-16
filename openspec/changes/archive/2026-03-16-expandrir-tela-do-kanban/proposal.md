# Proposal: Expand Kanban Screen on PC

## Problem Statement

Currently, when the Kanban board is viewed on a PC (desktop browser), it does not utilize the full screen width. This causes:

1. **Excessive horizontal scrolling** - Users must scroll horizontally to see all columns
2. **Poor use of screen real estate** - Large monitors are underutilized
3. **Poor UX** - The board feels cramped and requires constant horizontal navigation

## Root Cause Analysis

Examining `KanbanPage.tsx`, the following issues were identified:

1. **Container constraint**: The main container uses `sm:container sm:px-6 sm:py-10` which limits the width on desktop
2. **Fixed column width**: Each column is set to `w-[320px] shrink-0` (fixed 320px width)
3. **Horizontal overflow**: The board uses `overflow-x-auto` which enables horizontal scrolling
4. **min-w-max**: The column container uses `min-w-max` to force all columns to fit, causing overflow

## Proposed Solution

### 1. Remove Container Width Constraints
- Change `sm:container` to full viewport width
- Remove `sm:px-6` padding on the main container for desktop

### 2. Make Columns Responsive
- Use flexible width calculation instead of fixed 320px
- Implement responsive column sizing:
  - **Large screens (≥1440px)**: Calculate column width based on viewport (e.g., `w-[calc((100vw - 64px) / 8)]` for 8 columns)
  - **Medium screens (≥1024px)**: Allow columns to shrink below 320px or reduce number of visible columns
  - **Small desktop (1024px-1439px)**: Use percentage-based or flexible width

### 3. Optimize Horizontal Layout
- Remove or adjust `overflow-x-auto` behavior
- Consider using CSS Grid with `minmax()` for better flexibility
- Implement horizontal scroll only when necessary (truly narrow screens)

### 4. Responsive Strategy
- On **PC**: Show all columns without horizontal scroll, utilizing full viewport width
- On **Tablet**: Allow horizontal scroll but with better column sizing
- On **Mobile**: Keep current mobile-first behavior (existing)

## Success Criteria

1. ✅ On PC (≥1024px width), all 8 Kanban columns are visible without horizontal scrolling
2. ✅ The board utilizes the full available viewport width on desktop
3. ✅ Column cards maintain readability with appropriate width
4. ✅ No regression on mobile/tablet behavior
5. ✅ Smooth user experience without layout shifts

## Technical Approach

- Modify Tailwind CSS classes in `KanbanPage.tsx`
- Use CSS `calc()` or viewport units for responsive column sizing
- Test across different viewport sizes (1024px, 1280px, 1440px, 1920px)
- Ensure no breaking changes to existing functionality (drag-drop, card editing, etc.)

## Impact Assessment

- **Low risk**: Only UI/layout changes, no backend changes
- **No breaking changes**: Existing functionality preserved
- **Quick implementation**: Single component modification
