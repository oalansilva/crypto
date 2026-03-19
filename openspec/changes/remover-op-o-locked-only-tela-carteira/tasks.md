## 1. Frontend — Remove Locked Only Toggle

- [x] 1.1 Remove `lockedOnly` state and `setLockedOnly` from `ExternalBalancesPage.tsx`
- [x] 1.2 Remove "Locked only" toggle from the filter bar UI
- [x] 1.3 Remove `lockedOnly` from the `useEffect` dependency array that filters items
- [x] 1.4 Remove `lockedUsd` summary computation and its display in the summary section

## 2. Frontend — Remove Locked Column

- [x] 2.1 Remove `locked` from the table headers array (`headers`)
- [x] 2.2 Remove the "Locked" `<th>` cell from the desktop table
- [x] 2.3 Remove the locked value rendering from the desktop table row
- [x] 2.4 Remove the locked value rendering from the mobile card view
- [x] 2.5 Remove "Locked" from mobile column labels

## 3. Tests

- [x] 3.1 Update `external-balances.spec.ts` — remove any "locked only" filter assertions
- [x] 3.2 Verify no other tests reference `lockedOnly` or the "Locked" column

> 💡 Use the frontend/playwright skill when running E2E tests.
