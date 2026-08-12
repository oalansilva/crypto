from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"


def _load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


benchmark = _load_script("backend_unit_benchmark", "benchmark_backend_unit_tests.py")
inventory = _load_script("backend_unit_inventory", "validate_backend_unit_inventory.py")
unit_conftest = _load_script("backend_unit_conftest", "../backend/tests/unit/conftest.py")


def test_inventory_matches_all_unit_test_files():
    result = inventory.validate_inventory(
        ROOT,
        ROOT / "backend/tests/unit/test_inventory.json",
    )
    assert result["discovered_files"] == result["inventory_entries"] == 57


def test_inventory_rejects_missing_stale_and_duplicate_entries(tmp_path):
    fixture_root = tmp_path
    unit_dir = fixture_root / "backend/tests/unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_one.py").write_text("def test_one(): pass\n", encoding="utf-8")
    inventory_path = fixture_root / "inventory.json"
    inventory_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "file": "backend/tests/unit/test_stale.py",
                        "protected_behavior": "stale",
                        "production_reachability": "removed",
                        "persistence_need": "pure",
                        "regression_risk": "low",
                        "decision": "keep",
                        "evidence": "fixture",
                    },
                    {
                        "file": "backend/tests/unit/test_stale.py",
                        "protected_behavior": "stale",
                        "production_reachability": "removed",
                        "persistence_need": "pure",
                        "regression_risk": "low",
                        "decision": "keep",
                        "evidence": "fixture",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(inventory.InventoryValidationError, match="missing|stale|duplicate"):
        inventory.validate_inventory(fixture_root, inventory_path)


def test_inventory_rejects_broad_markers_and_unsafe_persistence_paths(tmp_path):
    fixture_root = tmp_path
    unit_dir = fixture_root / "backend/tests/unit"
    unit_dir.mkdir(parents=True)
    (unit_dir / "test_bad.py").write_text(
        """import pytest
pytestmark = pytest.mark.postgres

def test_bad():
    create_engine(\"postgresql://postgres:postgres@localhost/postgres\")
""",
        encoding="utf-8",
    )
    inventory_path = fixture_root / "inventory.json"
    inventory_path.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "file": "backend/tests/unit/test_bad.py",
                        "protected_behavior": "fixture",
                        "production_reachability": "reachable",
                        "persistence_need": "postgres",
                        "regression_risk": "high",
                        "decision": "keep",
                        "evidence": "fixture",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        inventory.InventoryValidationError,
        match="module-level postgres marker|shared /postgres URL",
    ):
        inventory.validate_inventory(fixture_root, inventory_path)


def test_inventory_semantics_match_current_fixture_contract():
    result = inventory.validate_inventory(
        ROOT,
        ROOT / "backend/tests/unit/test_inventory.json",
    )
    assert result["semantic_issues"] == []


def test_benchmark_parser_reports_required_metrics(tmp_path):
    junit = tmp_path / "junit.xml"
    junit.write_text(
        """<testsuites><testsuite name='unit' tests='3' time='1.25'>
          <testcase classname='alpha' file='backend/tests/unit/test_alpha.py' time='0.25'/>
          <testcase classname='alpha' file='backend/tests/unit/test_alpha.py' time='0.50'>
            <skipped/>
          </testcase>
          <testcase classname='beta' file='backend/tests/unit/test_beta.py' time='0.50'/>
        </testsuite></testsuites>""",
        encoding="utf-8",
    )
    log = tmp_path / "pytest.log"
    log.write_text(
        "================ 1 skipped, 7 warnings in 1.25s ================\n", encoding="utf-8"
    )
    summary = benchmark.build_summary(junit, pytest_log=log, revision="abc", environment="test")
    assert summary["collected_cases"] == 3
    assert summary["total_duration_seconds"] == 1.25
    assert summary["file_duration_p95_seconds"] == 0.75
    assert summary["slowest_files"][0]["file"].endswith("test_alpha.py")
    assert summary["skips"] == 1
    assert summary["warnings"] == 7


def test_ci_uses_one_bounded_unit_session_and_uploads_evidence():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    unit_job = workflow.split("  backend-unit-tests:", 1)[1].split("  backend-tests:", 1)[0]
    assert "timeout-minutes: 30" in unit_job
    assert "timeout 20m coverage run --parallel-mode" in unit_job
    assert "-m pytest -vv --durations=20" in unit_job
    assert "backend/tests/unit" in unit_job
    assert "junit.xml" in unit_job
    assert "timing.json" in unit_job
    assert "for test_file in backend/tests/unit/test_*.py" not in unit_job


def test_ci_preserves_pytest_status_and_reports_failures():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    unit_job = workflow.split("  backend-unit-tests:", 1)[1].split("  backend-tests:", 1)[0]
    coverage_step = unit_job.split("      - name: Upload backend unit coverage data", 1)[1].split(
        "      - name: Upload backend unit timing evidence", 1
    )[0]
    assert "set +e" in unit_job
    assert 'pytest_status="${PIPESTATUS[0]}"' in unit_job
    assert "if [[ -s test-artifacts/backend-unit/junit.xml ]]" in unit_job
    assert 'exit "${pytest_status}"' in unit_job
    assert '"missing_or_empty_junit"' in unit_job
    assert '"benchmark_failed"' in unit_job
    assert "if: always()" in coverage_step


def test_database_helper_is_postgres_only_and_pure_path_is_noop():
    unit_conftest._assert_safe_unit_database(
        "postgresql://postgres:postgres@127.0.0.1:5432/crypto_app_test"
    )
    for forbidden in (
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
        "sqlite+pysqlite:///:memory:",
        "mysql://user:pass@localhost/test_db",
        "postgresql://postgres:postgres@127.0.0.1:5432/crypto_app",
    ):
        with pytest.raises(RuntimeError):
            unit_conftest._assert_safe_unit_database(forbidden)

    def fail_if_reset(*_args, **_kwargs):
        raise AssertionError("pure path attempted database reset")

    original = unit_conftest._reset_postgres_state
    unit_conftest._reset_postgres_state = fail_if_reset
    try:
        request = SimpleNamespace(node=SimpleNamespace(get_closest_marker=lambda _name: None))
        generator = unit_conftest._isolate_unit_databases.__wrapped__(request)
        next(generator)
        generator.close()
    finally:
        unit_conftest._reset_postgres_state = original
