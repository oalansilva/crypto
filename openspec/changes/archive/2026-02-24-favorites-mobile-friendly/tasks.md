## 1. Discovery & Baseline

- [x] 1.1 Review current `/favorites` implementation (FavoritesDashboard + related components) and identify layout pain points on 360–430px widths
- [ ] 1.2 Capture before screenshots (mobile + desktop) for quick regression comparison

## 2. Mobile Layout (Cards / Stack)

- [x] 2.1 Implement a mobile-only card/stack renderer for favorites (no horizontal scrolling)
- [x] 2.2 Ensure each card shows primary fields: symbol, template/strategy name, tier (or “No tier”), and current status
- [x] 2.3 Add collapsible section for secondary details (notes/params/metrics) on mobile

## 3. Mobile Actions (Touch-Friendly)

- [x] 3.1 Ensure primary actions meet minimum touch target sizing (>= 44x44px) on mobile
- [x] 3.2 Add/verify confirmation flow for destructive actions (delete) on mobile
- [x] 3.3 Verify action placement does not cause mis-taps (spacing, grouping, overflow menu if needed)

## 4. Responsive Filters / Search

- [x] 4.1 Make filters/search usable on mobile (no horizontal scrolling; controls wrap/stack)
- [x] 4.2 Verify filters/search remain usable and unchanged on desktop

## 5. Regression Checks

- [x] 5.1 Verify desktop layout is preserved at/above the desktop breakpoint
- [x] 5.2 Verify mobile layout across common widths (360/390/430) and that no horizontal scrolling appears
- [x] 5.3 Smoke test key flows: open favorites, filter/search, edit/update, delete with confirmation

## 6. Validation

- [x] 6.1 Run `openspec validate favorites-mobile-friendly --type change` and fix any issues

> Note: Use project skills (.codex/skills) for frontend work, debugging, and verification when applicable.
