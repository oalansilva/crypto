# QA UI Validation Checklist

Run this checklist before sending any change to Alan homologation.

## Desktop Validation
- [ ] Navigate to Kanban board
- [ ] Verify all columns render correctly
- [ ] Check cards display proper styling
- [ ] Verify click handlers work (cards open correctly)
- [ ] Test modal/drawer opens and closes

## Mobile Validation  
- [ ] Test responsive layout
- [ ] Verify horizontal scroll works
- [ ] Check touch interactions work

## Bug-Specific Validation (if change involves bugs)
- [ ] Verify bug cards appear in correct column
- [ ] Check bug cards have visual distinction (border/color)
- [ ] Verify clicking bug opens bug detail (not parent)
- [ ] Test toggle to show/hide bugs works
- [ ] Verify parent story link displays correctly

## General
- [ ] No console errors
- [ ] Tests pass (backend integration)
- [ ] Build succeeds
