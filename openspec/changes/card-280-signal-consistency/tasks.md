## 1. Backend temporal consistency

- [x] 1.1 Stop deep backtest from synthesizing `end_of_period` as a realized `signal_15m` exit while preserving real stop exits.
- [x] 1.2 Add helpers that reject cached favorite events outside candle coverage or older than the latest calculated signal.
- [x] 1.3 Apply temporally valid latest trade evidence when OpportunityService resolves HOLD/EXIT and validate refresh persistence.
- [x] 1.4 Add backend unit/integration coverage for active entry, valid exit and future exit.

## 2. Frontend signal and marker consistency

- [x] 2.1 Keep the opportunities endpoint as canonical card/row state and prevent historical trade probes from reclassifying it.
- [x] 2.2 Ensure signal resolution and ChartModal markers do not let invalid exits override an active entry.
- [x] 2.3 Add frontend tests for active buy, confirmed sell and future/stale exit behavior.
- [x] 2.4 Confirm existing `DESIGN.md` tokens remain unchanged in desktop/mobile behavior.

## 3. Validation and handoff

- [x] 3.1 Run focused backend/frontend tests, formatter/build and `openspec validate card-280-signal-consistency`.
- [x] 3.2 Run Codex review on the exact diff and resolve/classify findings.
- [x] 3.3 Run `/opsx:verify` equivalent and record implementation evidence.
- [x] 3.4 Integrate into `develop`, execute `./restart` and validate the served DEV scenario.

## 4. Legacy cache correction

- [x] 4.1 Filter invalid future exits from saved favorite trades in backend read responses while preserving the valid open entry.
- [x] 4.2 Update the results table and favorite analysis path to represent an open final operation without a synthetic exit row.
- [x] 4.3 Add backend/frontend regression coverage for legacy cached future exits and open-position rendering.
- [ ] 4.4 Review, verify, integrate into `develop`, restart DEV, regenerate favorite 9 and validate database plus served UI.

Use project skills in `.codex/skills` when applicable for testing, debugging, frontend validation and OpenSpec verification.
