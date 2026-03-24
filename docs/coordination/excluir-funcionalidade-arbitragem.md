# excluir-funcionalidade-arbitragem

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: **done** ✅
- QA: **blocked - server restart required** ⚠️
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

## QA Findings (2026-03-24 15:23 UTC)

### Validation Results:
1. ✅ **Frontend (Working Tree)**: `/arbitrage` route removed, no "Arbitragem" nav item, ArbitragePage.tsx deleted
2. ✅ **Frontend (Running)**: Nav correctly shows no Arbitragem item (Vite serves modified files)
3. ❌ **API (Running Server)**: `/api/arbitrage/spreads` returns 200 with live data
4. ✅ **Health check**: `/api/health` returns 200 OK

### Issue Found:
**Backend server NOT restarted after staging changes.**

The DEV agent correctly staged changes to remove arbitrage from api.py/main.py. However, uvicorn (PID 677767, started 2026-03-24 13:59) is still running the OLD committed code.

**Evidence:**
- `curl http://72.60.150.140:5173/api/arbitrage/spreads` → 200 with spreads data
- Backend process running from old commit (before staged changes)
- Grep confirms staged api.py has no arbitrage, but running server has old code

### Next Step:
1. DEV: Restart backend server to apply staged changes
2. DEV: Commit the staged changes after restart verification
3. QA: Re-validate to confirm `/api/arbitrage/spreads` returns 404

## Next actions
- [x] QA: validate the removal (PARTIAL - frontend OK, backend blocked by server restart)
- [ ] DEV: Restart backend server to apply staged changes
- [ ] DEV: Commit staged changes after restart verification
- [ ] QA: Re-validate after restart
