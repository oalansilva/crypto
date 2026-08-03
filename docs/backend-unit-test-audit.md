# Backend unit-test audit (card #366)

Status: QA evidence captured for PR #371.  The machine-readable inventory
is the source of truth: [`backend/tests/unit/test_inventory.json`](../backend/tests/unit/test_inventory.json).
This document is the human-readable companion and must be regenerated when a
unit-test file is added, renamed, or removed.

## Scope and baseline

- Change: `audit-optimize-backend-unit-tests`
- Baseline revision: `origin/develop@34033bb08542e88045b1ed21d7ea31a0265ae79a`
- Baseline suite: 56 `backend/tests/unit/test_*.py` files, 403 collected cases,
  399 passed and 4 optional skips in the reference run.
- Reference backend-unit-tests job median: **4m44s (284s)**.
- Reference green jobs: `30679761659` (4m36s), `30679509735` (4m42s),
  `30730631820` (4m44s), `30729738750` (4m47s), and `30730180304` (4m53s).
- Reference environment: GitHub Actions `ubuntu-latest`, Python 3.12,
  PostgreSQL 15 service, `coverage run --parallel-mode`, and the five-run
  wall-time comparison supplied with the card.
- Target: optimized median at or below **198.8s** (30% below 284s).
- Optimized PR runs on reviewed commit `ef18e81c`: **1m55s**, **1m49s**, and
  **1m57s**.  The median is **1m55s (115s)**, a **59.5% reduction** from the
  284s reference median.
- Current post-rollback inventory: **55** files. The routing-contract test
  from cards #362/#369 was intentionally removed and is not part of this
  backend behavior inventory.

The baseline runner started one `pytest`/coverage process per file.  The
optimized runner uses one coverage session for `backend/tests/unit`, retains
per-test timeout protection, and emits JUnit plus deterministic JSON timing
artifacts.  No test is removed because of age, name, or duration alone.

## Database isolation decision

`postgres` is an explicit test marker/fixture contract.  Current persistence
tests request `postgres_isolation` (and an explicit safe URL fixture) at the
case or fixture boundary; broad module-level markers are not used.  Only
those requests invoke the shared reset helper.  Pure tests do not create an
engine, create schemas, or truncate tables in that helper.  PostgreSQL tests
validate both database URLs as PostgreSQL and reject SQLite, non-PostgreSQL
URLs, forbidden runtime database names, and non-test database names.  They
create the known metadata and truncate each table with `RESTART IDENTITY
CASCADE` before the test.  Existing test-local sessions remain responsible
for their own transaction cleanup.

The SQLite-backed persistence cases (`test_combo_service_templates.py` and the
workflow migration contract) were moved to PostgreSQL; the latter uses a
private schema.  SQLite is not used by unit persistence tests.
Opportunity-service dataframe and in-memory service cases remain
pure fakes and do not request the PostgreSQL fixture.

The card-366 rework owner is the backend test-harness lane.  Background
services, combo templates, runtime worker schema setup, and opportunity
persistence cases use explicit case-level fixtures; their pure/mock cases do
not pay reset cost.  The inventory evidence records this split.  Performance
proof and final QA were completed on PR #371 without changing the reviewed
implementation commit.

## Portfolio decisions

Every discovered file has exactly one `keep`, `refactor/consolidate`, or
`remove` decision in the JSON inventory.  Current evidence supports **keep**
for all 55 files: each protects reachable backend behavior or a deliberate
negative contract, and no removal guardrail has been met.  The table below is
the generated audit index; details and evidence strings are in the JSON.

| Unit-test file | Persistence | Decision | Protected behavior / evidence |
| --- | --- | --- | --- |
| `test_admin_backfill_routes_removed.py` | pure | keep | Removed-route absence contract |
| `test_admin_user_management_routes.py` | postgres | keep | Admin CRUD/audit route fixture |
| `test_api_coverage.py` | pure | keep | API health/candles with fakes |
| `test_background_services.py` | postgres | keep | Job manager and monitor state |
| `test_batch_backtest_async_support.py` | pure | keep | Queue/store/task fakes |
| `test_binance_realtime_connector.py` | pure | keep | Connector retry/snapshot paths |
| `test_binance_realtime_snapshot_store.py` | pure | keep | Snapshot file round-trip |
| `test_binance_realtime_worker.py` | pure | keep | Worker orchestration fakes |
| `test_binance_spot_orders.py` | pure | keep | Spot order validation/signing |
| `test_binance_symbol_universe.py` | pure | keep | Symbol selection fallback |
| `test_canonical_candle_writer_script.py` | pure | keep | Writer lock/state contract |
| `test_chart_pattern_service.py` | pure | keep | Pattern detection frames |
| `test_cleanup_beta_test_users.py` | pure | keep | Cleanup policy/parser |
| `test_combo_optimizer_final_execution_mode.py` | pure | keep | Optimizer mode forwarding |
| `test_combo_service_templates.py` | postgres | keep | Template listing/seeding |
| `test_combo_short_execution.py` | pure | keep | Short trade execution |
| `test_combo_strategy_logic_parser.py` | pure | keep | Parser and signal guardrails |
| `test_database_and_auth.py` | postgres | keep | DB/auth/beta access |
| `test_deep_backtest_open_position.py` | pure | keep | Open-position backtest |
| `test_dev_restart_contract.py` | pure | keep | Dev restart safety |
| `test_gateway_and_agent_chat.py` | postgres | keep | Gateway/chat route contract |
| `test_glassnode_service.py` | pure | keep | Provider cache/error mapping |
| `test_incremental_loader_tail_priority.py` | pure | keep | Incremental loader ordering |
| `test_indicator_score_service.py` | pure | keep | Score rules and endpoint fake |
| `test_main_and_market_routes.py` | pure | keep | Market/lifespan routes |
| `test_market_data_providers_coverage.py` | pure | keep | Provider registry/fallbacks |
| `test_market_indicator_advanced_consumption.py` | pure | keep | Indicator hydration |
| `test_market_indicator_pivot_levels.py` | pure | keep | Pivot calculations |
| `test_market_indicator_tradingview_fixtures.py` | pure | keep | TradingView parity; optional skips retained |
| `test_metrics_suite.py` | pure | keep | Metrics edge cases |
| `test_monitor_telegram_alerts.py` | postgres | keep | Alert persistence/routes |
| `test_ohlcv_backfill_service.py` | pure | keep | Backfill provider flow |
| `test_ohlcv_backfill_store.py` | pure | keep | Backfill file state |
| `test_ohlcv_storage.py` | pure | keep | SQL contract through fake engine |
| `test_onchain_exchange_flow_service.py` | pure | keep | Exchange-flow enrichment |
| `test_onchain_metrics_route.py` | pure | keep | On-chain route errors |
| `test_onchain_mining_metric_service.py` | pure | keep | Mining metric enrichment |
| `test_opportunity_position_state.py` | pure | keep | Position-state decisions |
| `test_opportunity_service_coverage.py` | postgres | keep | Favorites/catalog persistence |
| `test_portfolio_route.py` | postgres | keep | Portfolio snapshots/KPIs |
| `test_retrospectives_flow.py` | postgres | keep | Workflow retrospective flow |
| `test_routes_and_file_services.py` | pure | keep | File/log/market routes |
| `test_runtime_status.py` | pure | keep | Runtime status sanitization |
| `test_runtime_worker_and_workflow_db.py` | postgres | keep | Workflow DB/runtime worker |
| `test_sentiment_binance_validation.py` | postgres | keep | Sentiment/Binance/workflow validation |
| `test_sequential_optimizer_coverage.py` | pure | keep | Optimizer checkpoints |
| `test_signal_history_writer.py` | pure | keep | Quality gates with fake sessions |
| `test_small_services_and_utils.py` | postgres | keep | Preferences/refresh services |
| `test_strategy_descriptions.py` | pure | keep | Public strategy copy |
| `test_strategy_transparency.py` | pure | keep | Transparency/redaction |
| `test_trade_explanations.py` | pure | keep | Trade explanation evidence |
| `test_user_exchange_credentials_and_indicators.py` | postgres | keep | Credential persistence |
| `test_wallet_stable_balances.py` | pure | keep | Stable balance normalization |
| `test_workflow_services.py` | postgres | keep | Workflow transitions/migration |
| `test_workflow_validation_and_helpers.py` | postgres | keep | Workflow validation/handoff |

## Skips and warnings

The four baseline skips are the optional dependency/fixture cases in
`test_market_indicator_tradingview_fixtures.py`.  They remain explicit and are
not hidden by a warning filter; the follow-up is to install/provision the
optional indicator dependency before changing the skip disposition.

Recurring Pydantic, datetime, SQLAlchemy, and NumPy warnings are retained in
the report.  The owner is the card-366 backend test-harness lane; disposition
is documented/unsuppressed pending QA follow-up, so task 4.1 does not claim
that upstream deprecations were fixed.  No blanket suppression was added.
The benchmark parser records the warning total from the pytest log and the
JUnit report records skips/failures per case.

## Reproduction commands

```bash
# Validate the exact inventory/filesystem match.
python scripts/validate_backend_unit_inventory.py --json

# Consolidated run (PostgreSQL URLs must point to the dedicated test DB).
mkdir -p artifacts/backend-unit
set -o pipefail
SECONDS=0
timeout 20m coverage run --parallel-mode --source=backend/app -m pytest \
  -vv --durations=20 --junitxml=artifacts/backend-unit/junit.xml \
  backend/tests/unit 2>&1 | tee artifacts/backend-unit/pytest.log
pytest_status=${PIPESTATUS[0]}
python scripts/benchmark_backend_unit_tests.py \
  --junit-xml artifacts/backend-unit/junit.xml \
  --pytest-log artifacts/backend-unit/pytest.log \
  --output artifacts/backend-unit/timing.json \
  --markdown-output artifacts/backend-unit/timing.md \
  --started-at 0 --finished-at "$SECONDS"
benchmark_status=$?
if [ "$pytest_status" -ne 0 ]; then exit "$pytest_status"; fi
exit "$benchmark_status"
```

The commands above preserve the test/timeout result even when the benchmark
can still summarize a partial JUnit/log.  The CI implementation additionally
creates fallback timing files when JUnit is absent or incomplete.

## Local implementation verification

The focused harness/CI contract run passed **8 tests in 0.27s**.  The
serial rework full run passed **403 tests and skipped 4** in **67.279s JUnit /
69.799s wall**, with **190 warnings** and the same four optional
TradingView/pandas-ta skips.  A first run exposed an interaction between
`pytest-timeout`'s signal cancellation and the runtime-worker signal test; the
timeout method was changed to the thread watchdog and the complete rerun was
green.  No assertion or product behavior changed.

The PostgreSQL integration run passed **150 tests and skipped 4** in **24.71s**.
Combining the successful unit and integration coverage artifacts produced
**78.46% total backend line coverage** (threshold 70%).  `diff-cover` against
`origin/develop` reported no `backend/app` lines in this infrastructure-only
diff, so the differential gate had no changed production lines to score.

The local timing artifact is generated at
`/tmp/card366-artifacts/rework-full-2/timing.json` (with matching JUnit/log/
Markdown files); CI will upload the same JSON/JUnit/log bundle from
`backend-unit-tests`.

## Final QA and performance evidence

All three comparable GitHub Actions attempts used the same reviewed commit,
Linux runner, Python 3.12, PostgreSQL 15, consolidated unit selection, and
coverage mode:

| Attempt | `backend-unit-tests` | Result |
| --- | ---: | --- |
| 1 | 1m55s | green |
| 2 | 1m49s | green |
| 3 | 1m57s | green |

The optimized median is **1m55s (115s)**.  Against the **4m44s (284s)**
reference median, the reduction is `(284 - 115) / 284 = 59.5%`, exceeding the
30% acceptance target.  Across the three attempts, backend integration tests,
the 70% coverage gate, OpenSpec validation, frontend checks, required
Playwright visual QA, and `qa-gate` all reached terminal success.  The complete
check history is available on [PR #371](https://github.com/oalansilva/crypto/pull/371/checks).

Code Review left two preventive, non-blocking guardrail observations for
future hardening: the inventory validator recognizes safe-URL fixtures as
isolation evidence even though current persistence entries also request the
reset fixture, and the CI records pytest's pipeline status but does not
separately fail on a rare `tee` write error.  Neither gap affected the observed
three green attempts or PostgreSQL isolation in the current inventory.
