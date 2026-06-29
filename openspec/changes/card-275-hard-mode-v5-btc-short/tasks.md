## 1. Governance

- [x] 1.1 Validate `DIRECTION=short` and `MIXED_DIRECTIONS_ALLOWED=false`.
- [x] 1.2 Create issue/card #275 and add it to Project 1.
- [x] 1.3 Set Project fields: `Status=In Progress`, `Tipo=Codigo`, `Frente=Backtest`, `Responsavel=Codex`, `Prioridade=P1`.
- [x] 1.4 Publish OpenSpec artifacts to issue #275 before technical execution.

## 2. T0 Snapshot

- [x] 2.1 Capture current BTC/USDT 1D Short favorites with required fields.
- [x] 2.2 Capture compatible Short templates, public mappings/descriptions, and Pine scripts.
- [x] 2.3 Revalidate all current Short favorites full-period with capital 100, 100% in/out, deep backtest.
- [x] 2.4 Record T0 artifact path and summary on issue #275.

## 3. Benchmarks

- [ ] 3.1 Build same-direction benchmarks: return, drawdown, Sharpe, profit factor, and Pareto set. Blocked: T0 found zero BTC/USDT 1D Short favorites, so the required same-direction benchmark set cannot be formed.
- [ ] 3.2 Build dynamic Short-compatible reference set and record discarded incompatible references.

## 4. Candidate Search

- [ ] 4.1 Execute Short-only adaptive cycles with materially distinct theses and template families.
- [ ] 4.2 Track executed final deep candidates, duplicate rejects, direction rejects, and chain-superiority rejects.
- [ ] 4.3 Stress finalists before any save.

## 5. Winners

- [ ] 5.1 Save and validate WINNER_1.
- [ ] 5.2 Recalibrate benchmarks and save/validate WINNER_2.
- [ ] 5.3 Recalibrate benchmarks and save/validate WINNER_3.
- [ ] 5.4 Recalibrate benchmarks and save/validate WINNER_4.
- [ ] 5.5 Recalibrate benchmarks and save/validate WINNER_5.

## 6. Artifacts and Closeout

- [ ] 6.1 Generate Pine Script for each valid winner.
- [x] 6.2 Run focused validation and OpenSpec validation.
- [ ] 6.3 Restart DEV if runtime code/mapping changed.
- [ ] 6.4 Integrate versioned artifacts into `develop` if required.
- [x] 6.5 Comment final evidence on issue #275 and move to `Done` only if 5/5 succeed or to an evidenced blocker state if allowed by contract.
