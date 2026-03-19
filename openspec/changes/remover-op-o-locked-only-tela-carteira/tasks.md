## 1. Frontend — Remove Locked Only Toggle

- [ ] 1.1 Remove `lockedOnly` state and `setLockedOnly` from `ExternalBalancesPage.tsx`
- [ ] 1.2 Remove "Locked only" toggle from the filter bar UI
- [ ] 1.3 Remove `lockedOnly` from the `useEffect` dependency array that filters items
- [ ] 1.4 Remove `lockedUsd` summary computation and its display in the summary section

## 2. Frontend — Remove Locked Column

- [ ] 2.1 Remove `locked` from the table headers array (`headers`)
- [ ] 2.2 Remove the "Locked" `<th>` cell from the desktop table
- [ ] 2.3 Remove the locked value rendering from the desktop table row
- [ ] 2.4 Remove the locked value rendering from the mobile card view
- [ ] 2.5 Remove "Locked" from mobile column labels

## 3. Tests

- [ ] 3.1 Update `external-balances.spec.ts` — remove any "locked only" filter assertions
- [ ] 3.2 Verify no other tests reference `lockedOnly` or the "Locked" column

> 💡 Use the frontend/playwright skill when running E2E tests.
