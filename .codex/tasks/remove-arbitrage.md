# Remove the arbitrage feature completely. This is a DEV task.

## Changes to make:

### Frontend (in /root/.openclaw/workspace/crypto/frontend/src/):

1. **App.tsx**: Remove the import `import ArbitragePage from './pages/ArbitragePage'` and remove the route `<Route path="/arbitrage" element={<ArbitragePage />} />`

2. **pages/ArbitragePage.tsx**: DELETE this entire file

3. **components/AppNav.tsx**: 
   - Remove from `strategyNavItems` array: `{ to: '/arbitrage', label: 'Arbitragem', icon: Zap }`
   - Remove from `resolvePageTitle` function: `if (pathname.startsWith('/arbitrage')) return 'Arbitragem'`
   - Remove unused import `Zap` from lucide-react if it's no longer used anywhere else

### Backend (in /root/.openclaw/workspace/crypto/backend/app/):

4. **api.py**: Remove the endpoint function `get_arbitrage_spreads` and its `@router.get("/arbitrage/spreads")` decorator (around lines 167-178). Also remove the import of `get_spreads_for_symbols` from arbitrage_spread_service in that function if it's no longer used.

5. **main.py**: 
   - Remove the import `from app.services.arbitrage_monitor import monitor_arbitrage_opportunities`
   - Remove `app.state.arbitrage_task = None` (line 178)
   - Remove `app.state.arbitrage_stop_event = stop_event` (line 179)
   - Remove the whole if block that starts with checking `arbitrage_monitor_enabled` (lines 182-185)
   - Remove the code that cancels/awaits `arbitrage_task` (around line 190)
   
6. **config.py**: Remove the line `arbitrage_monitor_enabled: str = "1"` (line 25)

7. **services/arbitrage_monitor.py**: DELETE this entire file

8. **services/arbitrage_spread_service.py**: DELETE this entire file

### Tests (in /root/.openclaw/workspace/crypto/tests/):

9. **test_arbitrage_spread_service.py**: DELETE this file
10. **test_arbitrage_spreads_api.py**: DELETE this file

### Docs:

11. **docs/qa-ui-checklist.md**: Remove the line `- [ ] Arbitrage (/arbitrage)` (line 15)

### Validation:

After all changes, run:
```
grep -rn "arbitrage" --include="*.py" --include="*.ts" --include="*.tsx" /root/.openclaw/workspace/crypto/frontend/src/ /root/.openclaw/workspace/crypto/backend/app/ /root/.openclaw/workspace/crypto/tests/
```
And:
```
grep -rn "arbitrage" /root/.openclaw/workspace/crypto/docs/qa-ui-checklist.md
```

Report what files were changed/deleted and any remaining references found.
