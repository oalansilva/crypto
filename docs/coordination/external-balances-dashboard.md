# external-balances-dashboard

## Status
- PO: done
- DEV: not started
- QA: not started
- Alan (Stakeholder): needs approval

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Add a dashboard to view external balances (starting with Binance Spot) via read-only API.
- Surface (mobile/desktop): Desktop-first (still usable on mobile).
- Defaults: Fetch is on-demand (no aggressive polling). Default sort: total desc.
- Route: `/external/balances`
- Data sources: Binance Spot account endpoint (server-side only).
- Persistence: Do not persist balances; snapshot only.
- UI columns: asset, free, locked, total (highlight locked > 0).
- Performance limits: Keep calls rate-limit friendly; optional brief cache if needed.
- Security: Secrets in server env vars only; never in frontend; do not log secrets.
- Non-goals: Trading, withdrawals, transfers, history/PnL.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/external-balances-dashboard/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/external-balances-dashboard/review-ptbr
- PR: (none)
- CI run: (n/a)

## Notes
- Requires server env vars: `BINANCE_API_KEY`, `BINANCE_API_SECRET`.
- Backend must ensure errors are clear when secrets are missing and must not log key/secret.
- OpenSpec validation: `openspec validate external-balances-dashboard --type change` ✅

## Next actions
- [x] PO: Confirm UI/UX (route name, table columns, sorting) + error states; lock acceptance.
- [ ] DEV: Implement backend endpoint + frontend page/route.
- [ ] QA: Add backend mock test + Playwright E2E for new page.
- [ ] Alan: Review/approve scope + confirm we should proceed with Binance read-only integration.
