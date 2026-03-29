# filtrar-sinais-apenas-buy-com-target-stop

## Status
- PO: done
- DEV: done
- QA: in progress
- Alan approval: approved
- Alan homologation: not reviewed

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Filter signals - only save BUY signals. When target/stop is hit, UPDATE the existing BUY signal instead of creating a SELL signal.
- Surface (mobile/desktop): Backend API + Frontend filters
- Defaults: SELL signals are not persisted; BUY signals are the only trade signals saved
- Data sources: signal_history table
- Persistence: Changes to backend/app/routes/signals.py

## Links
- OpenSpec viewer: /openspec/changes/filtrar-sinais-apenas-buy-com-target-stop/
- PR: https://github.com/oalansilva/crypto/pull/new/feature/card68-buy-only
- Branch: feature/card68-buy-only

## Notes
- Backend fix: SELL signals are now skipped in _save_signal_to_history()
- entry_price is set to None when signal is created (actual execution price set when position closes via separate update)
- All existing tests pass

## Next actions
- [ ] PO:
- [ ] DEV:
- [ ] QA: Verify SELL signals are not saved; verify BUY signals show exit_price and PnL when closed
- [ ] Alan:
