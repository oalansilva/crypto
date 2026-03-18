## Why

The current crypto dashboard lacks a consistent visual identity. Each page has different colors, fonts, and navigation patterns, creating a fragmented user experience. Additionally, the site is not fully responsive, making it difficult to use on mobile devices. Standardizing the visual language and ensuring responsive behavior will improve usability and professionalism.

## What Changes

- **New**: Unified design system with consistent colors, typography, and spacing
- **New**: Single navigation menu (hamburger on mobile, top bar on desktop) that works identically across all pages
- **Modified**: Update all 8 pages to use the new design system tokens
- **Modified**: Implement responsive layouts for all pages (mobile breakpoint at 768px)
- **BREAKING**: Remove page-specific color overrides and custom headers/menus

## Capabilities

### New Capabilities

- **design-system**: Define CSS variables for colors, typography, spacing, and component styles
- **responsive-layout**: Ensure all pages adapt correctly to mobile (< 768px), tablet (768-1024px), and desktop (> 1024px) viewports
- **unified-navigation**: Single navigation component that works consistently across all pages with hamburger menu on mobile

### Modified Capabilities

- (None - this is a new UI overhaul not covered by existing specs)

## Impact

- **Frontend**: All pages in `frontend/src/pages/` will be updated to use design tokens
- **Styling**: May require updates to Tailwind config and global CSS
- **Navigation**: `App.tsx` and `AppNav.tsx` will be modified to support unified navigation
- **Testing**: Visual regression tests should be updated to capture new design system
