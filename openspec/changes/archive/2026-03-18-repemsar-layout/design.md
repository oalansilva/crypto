## Context

The current crypto dashboard has inconsistent visual design across pages:
- Different color schemes per page
- Different header/menu implementations (some pages have custom headers)
- No unified navigation
- Poor mobile experience

This change establishes a design system and unified navigation to create a consistent experience.

## Goals / Non-Goals

**Goals:**
- Create CSS custom properties for colors, typography, spacing
- Ensure all pages use the design system tokens
- Implement unified navigation that works on all pages
- Make all pages responsive (mobile/tablet/desktop)

**Non-Goals:**
- Change the actual functionality of pages (only visual/styling changes)
- Add new pages
- Modify backend APIs

## Decisions

### 1. CSS Custom Properties over Tailwind-only
**Decision:** Use CSS custom properties (variables) in addition to Tailwind.
**Rationale:** Provides single source of truth for colors, easier to theme, consistent across all components.

### 2. Single AppNav Component
**Decision:** Use the existing AppNav component and ensure it's rendered on ALL pages.
**Rationale:** Avoids duplication, easier maintenance, consistent behavior.

### 3. Mobile Menu: Bottom Sheet Pattern
**Decision:** Use bottom sheet for mobile navigation menu.
**Rationale:** Better mobile UX than slide-out, easier to close by tapping outside.

### 4. Tailwind Config Extension
**Decision:** Extend Tailwind config with design tokens rather than replacing it.
**Rationale:** Keeps existing utilities working, easier migration.

## Risks / Trade-offs

- [Risk] Pages with custom headers may need refactoring
  - **Mitigation**: Identify all custom headers, refactor to use AppNav
- [Risk] Some page-specific overrides may break
  - **Mitigation**: Test all pages after changes, update overrides to use tokens
- [Risk] Responsive breakpoints may conflict with existing styles
  - **Mitigation**: Use Tailwind's built-in responsive classes, test on all breakpoints

## Migration Plan

1. Add CSS custom properties to global CSS
2. Update Tailwind config to use design tokens
3. Refactor pages with custom headers to use AppNav
4. Update AppNav for mobile hamburger menu
5. Update each page to use design tokens
6. Test all 8 pages on mobile, tablet, desktop
7. Deploy and verify
