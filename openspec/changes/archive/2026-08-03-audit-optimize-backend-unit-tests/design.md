## Context

Card #366 targets the `backend-unit-tests` GitHub Actions job. The five green runs immediately preceding the card were `30679761659` (4m36s), `30679509735` (4m42s), `30730631820` (4m44s), `30729738750` (4m47s), and `30730180304` (4m53s), for a 4m44s reference median. In run `30730631820`, pytest reported about 2m25s across the files. The current job loops over 56 files and starts `coverage run -m pytest` once per file. The unit-level autouse fixture also creates both SQLAlchemy schemas and truncates every application/workflow table before every test, including tests that never touch persistence.

The reference suite contains 399 collected cases from approximately 371 `test_*` functions, with 4 skips and 246 warnings in the cited run. Existing total and differential backend coverage gates are both 70%. PostgreSQL is mandatory for persistence tests; SQLite is not an accepted substitute.

`UI impact: none` because the change is confined to CI, backend test fixtures/configuration, test organization, and audit evidence. No product route, API contract, copy, component, or visual state changes.

## Goals / Non-Goals

**Goals:**

- Produce a reproducible before/after performance baseline, including total duration, p95, ten slowest files, collected cases, skips, and warnings.
- Give every unit-test file a traceable keep, refactor/consolidate, or remove decision tied to live production behavior and regression risk.
- Remove repeated pytest/coverage startup overhead and unnecessary PostgreSQL setup from pure tests.
- Preserve deterministic PostgreSQL isolation for tests that exercise persistence.
- Preserve actionable failure localization, bounded execution, and total/diff coverage gates of at least 70%.
- Demonstrate at least 30% median improvement across three comparable optimized runs, or prove the remaining bottleneck is outside the suite and open a specific follow-up action.

**Non-Goals:**

- Change runtime product behavior, APIs, database models, or UI.
- Replace PostgreSQL with SQLite.
- Delete tests because of age, naming, or duration alone.
- Lower coverage thresholds, silently ignore warnings, or skip required QA jobs.
- Introduce parallel database execution before per-worker isolation is proven safe.

## Decisions

### 1. Audit before consolidation or removal

The canonical machine-readable inventory will live at `backend/tests/unit/test_inventory.json`, with a generated human-readable audit at `docs/backend-unit-test-audit.md`. It will cover all files under `backend/tests/unit/test_*.py`. Each entry will record the production module/route/job or contract protected, current reachability, persistence need, decision, risk, and evidence. Removal requires proof that the behavior is unreachable/removed or equivalently covered elsewhere; otherwise the default is keep or refactor.

Alternative considered: delete files with names such as `*_removed.py` or `*_coverage.py`. Rejected because naming does not establish obsolete behavior or duplicate protection.

### 2. Measure through machine-readable test output

The optimized suite will emit machine-readable timing output (JUnit XML or an equivalent pytest report) and a small deterministic summarizer will aggregate per-file totals, file-duration p95, slowest files, cases, skips, failures, and warnings. Baseline commands, environment, revisions, and CI run links will be recorded beside the audit. The acceptance comparison uses the complete GitHub Actions `backend-unit-tests` job wall time: the 4m44s reference median above versus at least three post-change PR runs on the same Linux/PostgreSQL/coverage path.

Alternative considered: rely only on GitHub job wall time. Rejected because job time cannot separate runner startup, fixture cost, and test execution.

### 3. Use one coverage session for the unit suite

The CI job will invoke the unit directory in one pytest/coverage session rather than 56 independent sessions. It will keep verbose-enough progress and machine-readable output for failure localization, a per-test timeout mechanism, and the existing job-level timeout.

Alternative considered: parallelize files immediately. Rejected for the first iteration because the shared PostgreSQL database and global truncation strategy are not safe for concurrent workers without separate databases/schemas.

### 4. Make PostgreSQL isolation explicit and opt-in

The database reset logic will move behind an explicit `postgres` pytest marker/fixture for files or cases proven to use application/workflow persistence. Pure tests will not create schemas, open a database engine, or truncate tables. Marked tests will continue to use a dedicated PostgreSQL URL, reject SQLite and every non-PostgreSQL backend, enforce safety checks against runtime database names, create schemas, and reset tables.

The migration will classify and mark existing database-dependent tests before disabling the global autouse path. A full PostgreSQL unit and integration run is required to catch missing classifications.

Alternative considered: keep the global autouse reset and optimize only the CI loop. Rejected because pure tests would continue paying dominant setup cost and the card explicitly requires separating persistence needs.

### 5. Preserve quality gates and treat skips/warnings as inventory

Coverage artifacts remain compatible with the existing combine step, and both total and differential thresholds remain at least 70%. Every persistent skip and recurring warning category will be fixed or recorded with owner/rationale; filters may suppress only understood third-party noise and may not hide project regressions.

## Risks / Trade-offs

- **[Missing database marker causes order dependence or stale data]** → Classify all files first, retain database-name safety guards, run the complete unit suite in PostgreSQL repeatedly, and run integration tests before acceptance.
- **[Single pytest process exposes leaked global state]** → Treat resulting order failures as test-isolation defects; reset only the resource involved and keep deterministic ordering independent.
- **[Per-test timeout interrupts a legitimately slow case]** → Derive the threshold from measured p95/slowest cases, keep the job-level timeout, and document any justified case-specific override.
- **[Timing noise masks the real gain]** → Compare medians of equivalent Linux/PostgreSQL runs with the same test selection and coverage mode; retain raw command/run references.
- **[Coverage drops after consolidation]** → Compare combined total and diff coverage before/after and block acceptance below 70% or on unexplained loss.
- **[Audit becomes stale]** → Generate counts from the filesystem/collection and validate that every discovered file has exactly one audit row.

## Migration Plan

1. Capture the current reference metrics and generate the 56-file audit inventory.
2. Classify persistence-dependent tests and introduce explicit PostgreSQL isolation without changing test assertions.
3. Consolidate the CI runner into one bounded coverage session and add machine-readable timing evidence.
4. Refactor/consolidate or remove tests only where the audit evidence satisfies the removal guardrail; resolve/classify skips and warnings.
5. Run focused harness tests, the full unit suite, integration suite, coverage gates, OpenSpec validation, and three comparable performance runs.
6. If isolation or coverage regresses, revert to the per-file runner/global reset while preserving the audit evidence for a narrower follow-up.

## Open Questions

- Which files, if any, have enough evidence for removal rather than keep/refactor?
- What per-test timeout best fits the measured slowest legitimate case?
- Which warning categories originate in project code versus pinned third-party dependencies?

## Prototype

N/A — `UI impact: none`; the change creates no visual surface and changes no existing screen.

## Design Critique

**Scope/product:** The design changes only CI and test infrastructure. It does not alter runtime behavior or introduce an unclassified visual surface. The audit-first rule protects useful negative regressions such as `test_admin_backfill_routes_removed.py` from deletion based on naming.

**Regression protection:** The initial proposal left the audit artifact and comparison metric underspecified. Corrected by defining `backend/tests/unit/test_inventory.json`, generated `docs/backend-unit-test-audit.md`, file-duration p95, and the exact five-run 4m44s wall-time reference median. Coverage, PostgreSQL integration tests, visual QA, and `qa-gate` remain mandatory.

**Operational risk:** Static inspection found that the current function-scoped autouse fixture can perform schema creation/truncation up to 403 times, while only 17 files directly reference SQLAlchemy/database APIs. Direct-reference counts are not sufficient to classify indirect dependencies, so the design requires a complete audit, explicit marker migration, focused fixture tests, repeated full-suite runs, and rollback before disabling global isolation.

**Database safety:** The existing helper permits SQLite despite the project contract. The design now requires marked persistence tests to reject SQLite/non-PostgreSQL backends and retain dedicated test-database name guards.

**Runner/timeouts:** Consolidating into one process can expose leaked imports/caches and would remove the current per-file 180s timeout. The design keeps a job timeout, adds a measured per-test timeout, preserves identifying output, and deliberately defers parallelism until database isolation supports it.

**Skips/warnings:** Four observed skips depend on optional indicator packages, while repeated Pydantic/datetime/SQLAlchemy/NumPy warnings include both real debt and per-process duplication. The design requires classification/fix before any narrow suppression; no blanket filter is accepted.

**Prototype:** N/A — `UI impact: none`; no screen, component, copy, route, or visual state changes.

No blocking design finding remains. Non-blocking implementation decisions are limited to the measured timeout value and whether evidence supports any individual consolidation/removal.

Design Agent verdict: PASS
