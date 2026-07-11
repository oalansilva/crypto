## 1. Governance preflight

- [x] Validate `DIRECTION=short`, `DIRECTION_LABEL=SHORT`, and `MIXED_DIRECTIONS_ALLOWED=false`.
- [x] Create GitHub issue/card #276 automatically and add it to Project 1.
- [x] Set Project 1 fields: `Status=In Progress`, `Tipo=Codigo`, `Frente=Backtest`, `Responsavel=Codex`, `Prioridade=P1`.
- [x] Publish this OpenSpec package to #276 before technical execution.

## 2. T0 and benchmark setup

- [x] Capture timestamped T0 snapshot for BTC/USDT 1d SHORT before optimization/backtest/save/template mutation/Pine generation.
- [x] Record current Favorites by direction, SHORT Favorites, compatible templates, public mappings, Pine scripts, and API/tela metrics.
- [x] Revalidate all current SHORT Favorites with Deep Backtest, 100 USD, 100% entry/exit, no partial exits, no pyramiding, full-period. T0 had zero current SHORT Favorites, so `COLD_START_MODE=true` and no same-direction Favorite required revalidation.
- [x] Set benchmark fields or `COLD_START_MODE=true` if same-direction benchmarks are absent.

## 3. Candidate search and sequential saves

- [x] Verify the engine/API supports true SHORT execution with required capital, sizing, and Deep Backtest before counting any winner.
- [x] Execute direction-compatible theses/templates/candidates until five sequential winners are found or a real blocker satisfies all thresholds.
- [x] For every candidate, enforce anti-duplicate, anti-dominance, robustness, OOS/stress, trade-count, and public-name pre-save gates.
- [x] Save and validate WINNER_1 in Favorites.
- [x] Recalibrate benchmarks and chain after WINNER_1.
- [x] Save and validate WINNER_2 in Favorites.
- [x] Recalibrate benchmarks and chain after WINNER_2.
- [x] Save and validate WINNER_3 in Favorites.
- [x] Recalibrate benchmarks and chain after WINNER_3.
- [x] Save and validate WINNER_4 in Favorites.
- [x] Recalibrate benchmarks and chain after WINNER_4.
- [x] Save and validate WINNER_5 in Favorites.

## 4. Versioned artifacts and closeout

- [x] Generate versioned Pine Script for each accepted SHORT winner.
- [x] Generate final evidence report with T0, benchmarks, cold-start state, references, rankings, winner proofs, payload summaries, and fallback-negative checks.
- [x] If code changes occur, run focused tests, Codex review, commit, integrate into `develop`, execute `./restart`, and validate served API/tela.
- [x] Run OpenSpec validation for this change and proportional technical checks.
- [x] Comment final evidence in #276 and move to `Status=Done` only after five valid winners are saved and validated, or report a contract-compliant blocker.
