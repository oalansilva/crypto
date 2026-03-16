# Tasks: Expand Kanban Screen on PC

## Implementation Tasks

### Task 1: Remove Container Width Constraint
**File**: `frontend/src/pages/KanbanPage.tsx`

- [ ] Remove `sm:container` class from the main `<main>` element
- [ ] Remove `sm:px-6 sm:py-10` padding classes from the main container
- [ ] Verify full viewport width is utilized on desktop

**Current code**:
```tsx
<main className="mx-auto px-0 py-0 sm:container sm:px-6 sm:py-10">
```

**Target**: Use full viewport width without container constraints

---

### Task 2: Make Column Widths Responsive
**File**: `frontend/src/pages/KanbanPage.tsx`

- [ ] Replace fixed `w-[320px]` with responsive width calculation
- [ ] Use viewport-based width for large screens (≥1280px)
- [ ] Implement CSS `calc()` for dynamic column sizing

**Current code**:
```tsx
className={'w-[320px] shrink-0 rounded-xl border bg-zinc-900/40...'}
```

**Target**: Columns should scale based on viewport width to show all columns

---

### Task 3: Optimize Horizontal Layout Behavior
**File**: `frontend/src/pages/KanbanPage.tsx`

- [ ] Review `overflow-x-auto` on the board container
- [ ] Adjust to minimize horizontal scroll on larger viewports
- [ ] Ensure scroll only appears on truly narrow screens

**Current code**:
```tsx
<div className="overflow-x-auto">
  <div className="flex items-start gap-4 min-w-max pb-2">
```

**Target**: Horizontal scroll should be unnecessary on PC

---

### Task 4: Test Responsive Behavior
**Files to verify**: `frontend/src/pages/KanbanPage.tsx`

- [ ] Test at 1024px width (small desktop)
- [ ] Test at 1280px width (standard laptop)
- [ ] Test at 1440px width (large desktop)
- [ ] Test at 1920px width (wide monitor)
- [ ] Verify all 8 columns are visible without horizontal scroll
- [ ] Verify card content remains readable

---

### Task 5: Verify Existing Functionality
**Files to verify**: `frontend/src/pages/KanbanPage.tsx`

- [ ] Drag and drop between columns still works
- [ ] Card selection and editing still works
- [ ] Mobile layout not affected
- [ ] No visual regressions

---

## QA Checklist

- [ ] Desktop (≥1024px): All 8 columns visible without horizontal scroll
- [ ] Desktop (≥1280px): Full viewport width utilized
- [ ] Cards have readable width (not too compressed)
- [ ] Mobile view unchanged
- [ ] Drag-drop functional
- [ ] No console errors

## Notes

- Tailwind CSS is used for styling
- The board has 8 columns: Pending, PO, DESIGN, Alan approval, DEV, QA, Alan homologation, Archived
- Current column width is 320px × 8 = 2560px minimum - which exceeds most laptop screens
- Solution should scale columns appropriately based on viewport
