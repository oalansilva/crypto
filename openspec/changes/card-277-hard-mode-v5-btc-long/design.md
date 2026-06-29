## Context

The execution is an operational discovery run, not a broad product redesign. Existing APIs, database tables, optimizer behavior, and Favorites UI should be reused. Code changes are only allowed if the run exposes a product bug that blocks the contract, such as public-name fallback or missing direction persistence.

## Decisions

- Use `BTC/USDT`, `1d`, `direction=long` for every benchmark, candidate, Favorite, and Pine artifact.
- Treat empty same-direction benchmarks as cold-start, not a blocker. In cold-start, Winner 1 initializes the chain and Winner 2-5 must improve sequentially against saved winners.
- Count only final unique Deep Backtest executions as material candidates. Optimizer stages, duplicate parameter sets, non-deep runs, renames, revalidations, and wrong-direction strategies do not count.
- Recalibrate after each saved winner by reading back the Favorite through the database/API and recomputing the current chain/Pareto set before testing the next slot.
- Store durable execution artifacts in the repo only after this OpenSpec change exists. Temporary scratch output may be used for computation, but final evidence and Pine exports must be versioned if used for closeout.
- Keep `main` untouched because `PROD_RELEASE=false`. Technical completion means validated artifacts integrated into `develop`, followed by `./restart` and card evidence.

## Evidence Model

- T0 snapshot: timestamp, current BTC/USDT 1d Long Favorites, direction counts, templates, public mappings, related Pine files, and revalidated same-direction favorites when present.
- Candidate ledger: cycles, theses, template families, material deep candidates, finalist stress tests, duplicate/direction/dominance rejects, and current chain benchmark before each slot.
- Winner records: Favorite id, created_at, direction, public name/copy, strategy key, parameters, full-period metrics, OOS/stress evidence, save payload, backtest payload, readback proof, and Pine path.
- Final report: 5/5 status or blocker budget/evidence, plus negative proof that new Favorite ids never resolve as `Estratégia Cripto Farol`.

## Risks

- Long-running optimization may exceed one interactive turn. The card remains the authoritative progress trail if continuation is required.
- New strategy keys may need public mapping changes. If so, update the mapping path before save, run focused tests, restart, and re-read the served API.
- Existing stale OpenSpec changes may affect global validation. Validate this change directly as intermediate evidence and address global hygiene before Done/release workflow steps.
