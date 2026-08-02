## 1. Baseline and Audit Evidence

- [x] 1.1 Add a deterministic benchmark/report command that aggregates machine-readable pytest output into collected cases, total duration, per-file totals, p95, ten slowest files, skips, and warnings.
- [x] 1.2 Record the five green reference CI runs, environment/revision, raw timing evidence, and baseline median used for the 30% target.
- [x] 1.3 Create the complete inventory for every `backend/tests/unit/test_*.py` file with protected behavior, production reachability, persistence need, regression risk, decision, and evidence.
- [x] 1.4 Add a validation check that fails when a discovered unit-test file is missing from the inventory or the inventory contains a stale/duplicate entry.

## 2. PostgreSQL Isolation

- [x] 2.1 Refactor the unit-test database reset behind an explicit `postgres` marker/fixture while rejecting SQLite/non-PostgreSQL URLs and preserving dedicated test-database safety checks, schema setup, and deterministic truncation.
- [x] 2.2 Mark every database-dependent unit file/case identified by the audit and prove that pure tests do not create engines, schemas, or truncate tables.
- [x] 2.3 Add focused regression tests for pure-test no-DB behavior, marked PostgreSQL isolation, forbidden runtime database names, and repeated-suite/order safety.

## 3. Low-Overhead CI Runner

- [x] 3.1 Configure a justified per-test timeout and retain the job-level timeout with actionable test progress/failure output.
- [x] 3.2 Replace the 56 per-file pytest/coverage launches with one consolidated unit-directory coverage session.
- [x] 3.3 Upload compatible coverage data plus raw timing/report artifacts from `backend-unit-tests` and add/update workflow contract tests.

## 4. Test Portfolio Cleanup

- [x] 4.1 Resolve or document every persistent skip and recurring warning category without hiding project failures.
- [x] 4.2 Refactor/consolidate redundant or misplaced tests identified by the audit while preserving the protected behavior.
- [x] 4.3 Remove tests only where the audit proves removed/unreachable behavior or equivalent remaining coverage, and update the inventory evidence.

## 5. Verification and Performance Proof

- [x] 5.1 Run focused harness/configuration tests and the complete backend unit suite against PostgreSQL until green.
- [x] 5.2 Run backend integration tests against PostgreSQL and verify combined total and differential coverage remain at least 70%.
- [ ] 5.3 Record at least three comparable optimized runs and prove a median improvement of at least 30%, or isolate the external bottleneck and create/link the required follow-up action.
- [ ] 5.4 Run OpenSpec validation, required Playwright visual QA, `qa-gate`, and document the final audit table, commands, timings, coverage, and CI links on card #366.
