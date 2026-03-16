# Proposal: Visual Distinction for Bug Items on Kanban Board

## Problem Statement

Currently, all items on the Kanban board are displayed with the same visual styling, regardless of their type. This makes it difficult for users to quickly identify bug items among other item types (stories, changes, etc.). The lack of visual separation creates a UX issue where:

- Bug items can be easily overlooked
- Users must read each card's content to determine if it's a bug
- The board lacks visual hierarchy for different item types

## Problem 2: Bug Creation Workflow

Currently, there's no standardized process for creating bugs when QA finds issues:
- QA finds a bug but has no clear workflow to create it
- Stories can be closed without addressing all related bugs
- Bugs don't go through the full Kanban flow (DEV → QA → homologation)

## Proposed Solution

### Part 1: Visual Distinction for Bugs
Implement a color-coding system to visually distinguish bug items from other item types on the Kanban board. This will provide immediate visual recognition of bug items without requiring users to read the card content.

### Part 2: Bug Creation Workflow
Implement a standardized bug creation workflow:
1. When QA finds a bug, they add a comment on the story describing the bug
2. QA creates a new "bug" type work item linked to the story
3. The story cannot be finalized until all child bugs are resolved
4. Bugs go through the full Kanban flow: DEV → QA → homologation

### Key Design Decisions

1. **Distinct Bug Color**: Apply a unique background color to bug item cards
   - Suggested: Red/coral tone (e.g., `#FF6B6B` or `#E53E3E`) to convey "issue/attention needed"
   - Alternative consideration: Could use purple/red-mix for bug-specific branding

2. **Visual Treatment Options**:
   - Background color change for the entire card
   - Colored left border/strip on each card
   - Badge/icon indicator for bug type
   - Combination of above (recommended: border + subtle background)

3. **Consistency**: Apply the same styling across all Kanban columns (Pending, PO, Dev, QA, Homolog, Done)

4. **Accessibility**: Ensure sufficient contrast ratio for readability

## Impact Analysis

- **Frontend**: CSS/UI component changes + bug creation form
- **Backend**: API endpoint to create bug items linked to stories
- **Database**: May need to add parent_link field to work_items
- **User Experience**: High positive impact - faster item identification + clear bug workflow

## Success Criteria

- Bug items are immediately identifiable by color on the board
- No impact on other item types' display
- Consistent visual treatment across all columns
- Meets accessibility contrast requirements
