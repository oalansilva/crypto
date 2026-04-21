# QA UI Validation Checklist

Run this checklist before sending any change to Homologation.

## ⚠️ Before Testing - MANDATORY
- [ ] **Run `./stop.sh && ./start.sh`** to ensure clean state and avoid cache issues

## Mobile Validation (REQUIRED for responsive/mobile changes)
- [ ] Test on mobile viewport (375px width) for ALL pages:
  - [ ] Home (/)
  - [ ] Favorites (/favorites)
  - [ ] Monitor (/monitor)
  - [ ] Combo (/combo/select)
  - [ ] Carteira (/external/balances)
- [ ] Verify NO duplicate headers/menus appear on ANY page
- [ ] Open hamburger/bottom-sheet menu on EACH page
- [ ] Verify menu is readable (good contrast, no transparency issues)
- [ ] Verify NO overlap/conflicts with page content
- [ ] Take screenshots of each test case

## Desktop Validation
- [ ] Validate every changed/critical route for desktop rendering and interactions
- [ ] Test modal/drawer behavior on changed flows
- [ ] Verify no responsive regressions on impacted desktop views

## Mobile Validation  
- [ ] Test responsive layout
- [ ] Verify horizontal scroll works
- [ ] Check touch interactions work

## Bug-Specific Validation (if change involves bugs)
- [ ] Verify bug states appear correctly in the relevant UI
- [ ] Verify bug details render in correct context (parent/child hierarchy)
- [ ] Test bug toggles and filters if UI exposes them

## General
- [ ] No console errors
- [ ] Tests pass (backend integration)
- [ ] Build succeeds
