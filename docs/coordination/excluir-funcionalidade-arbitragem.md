# excluir-funcionalidade-arbitragem

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: **done** ✅
- QA: not started
- Alan homologation: not reviewed

## DEV Handoff
- Feature branch: `feature/card49-remove-arbitrage`
- Changes committed to git index (staged)

### What was done (Card #49):
**Frontend:**
- Removed `/arbitrage` route from `frontend/src/App.tsx`
- Deleted `frontend/src/pages/ArbitragePage.tsx`
- Removed `{ to: '/arbitrage', label: 'Arbitragem', icon: Zap }` from `strategyNavItems` in `frontend/src/components/AppNav.tsx`
- Removed `if (pathname.startsWith('/arbitrage')) return 'Arbitragem'` from `resolvePageTitle()`
- Zap icon correctly kept in `StrategyBuilder.tsx` (used for 'momentum' strategy)

**Backend:**
- Removed `@router.get("/arbitrage/spreads")` endpoint from `backend/app/api.py`
- Removed `arbitrage_monitor_enabled` config from `backend/app/config.py`
- Removed `monitor_arbitrage_opportunities` import and startup logic from `backend/app/main.py`
- Removed unused `asyncio` import from `backend/app/main.py`
- Deleted `backend/app/services/arbitrage_monitor.py`
- Deleted `backend/app/services/arbitrage_spread_service.py`

**Tests & Docs:**
- Deleted `tests/test_arbitrage_spread_service.py`
- Deleted `tests/test_arbitrage_spreads_api.py`
- Removed `- [ ] Arbitrage (/arbitrage)` from `docs/qa-ui-checklist.md`

**Validation:**
- `grep -rn "arbitrage"` in frontend/backend/tests: no matches ✅
- `grep -n "arbitrage"` in qa-ui-checklist.md: no matches ✅
- All arbitrage files deleted ✅

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/excluir-funcionalidade-arbitragem/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/excluir-funcionalidade-arbitragem/review-ptbr

## Next actions
- [ ] QA: validate the removal (navigate UI, check /arbitrage route returns 404, check /api/arbitrage/spreads returns 404)
