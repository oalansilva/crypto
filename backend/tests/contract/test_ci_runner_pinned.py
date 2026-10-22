"""Contract: CI runs on a pinned runner image (card #1133, design D5).

Pure text checks (no PyYAML) so the guard runs in ``backend-unit-tests``, a
dependency of ``qa-gate``, without touching ``ci.yml`` logic.

Changing the pinned label requires its own card decided by Alan: edit
``PINNED_RUNNER`` in a visible diff.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS_DIR = ROOT / ".github/workflows"
GITHUB_DIR = ROOT / ".github"
CI_WORKFLOW = WORKFLOWS_DIR / "ci.yml"
FRONTEND_PACKAGE = ROOT / "frontend/package.json"
FRONTEND_LOCKFILE = ROOT / "frontend/package-lock.json"

PINNED_RUNNER = "ubuntu-24.04"
FORBIDDEN_RUNNER_LABEL = "ubuntu-latest"

_RUNS_ON_RE = re.compile(r"^(?P<indent>\s*)runs-on:\s*(?P<value>.*?)\s*$")
_JOB_KEY_RE = re.compile(r"^  (?P<job>[A-Za-z0-9_][A-Za-z0-9_-]*):\s*(?:#.*)?$")
_EXACT_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def _strip_comment(value: str) -> str:
    return value.split(" #", 1)[0].strip()


def _unquote(value: str) -> str:
    value = _strip_comment(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def find_runner_violations(
    text: str,
    filename: str,
    *,
    pinned: str = PINNED_RUNNER,
    require_runs_on_in_every_job: bool = False,
) -> list[str]:
    """Return one message per ``runs-on`` that is not literally ``pinned``.

    With ``require_runs_on_in_every_job`` every job under the top-level
    ``jobs:`` key must declare ``runs-on`` too.
    """
    violations: list[str] = []
    in_jobs = False
    current_job: str | None = None
    jobs_with_runs_on: set[str] = set()
    all_jobs: list[str] = []

    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^jobs:\s*(?:#.*)?$", line):
            in_jobs = True
            current_job = None
            continue
        if in_jobs and re.match(r"^\S", line) and not line.startswith("#"):
            in_jobs = False
            current_job = None
        if in_jobs:
            job_match = _JOB_KEY_RE.match(line)
            if job_match:
                current_job = job_match.group("job")
                all_jobs.append(current_job)

        runs_on = _RUNS_ON_RE.match(line)
        if not runs_on:
            continue
        value = _unquote(runs_on.group("value"))
        where = f"{filename}:{number}" + (f" job={current_job}" if current_job else "")
        if value != pinned:
            violations.append(f"{where}: runs-on must be literally '{pinned}', found '{value}'")
        if current_job:
            jobs_with_runs_on.add(current_job)

    if require_runs_on_in_every_job:
        for job in all_jobs:
            if job not in jobs_with_runs_on:
                violations.append(f"{filename} job={job}: missing runs-on")
    return violations


def find_forbidden_label_lines(
    text: str, filename: str, *, forbidden: str = FORBIDDEN_RUNNER_LABEL
) -> list[str]:
    return [
        f"{filename}:{number}: '{forbidden}' is not allowed anywhere under .github/"
        for number, line in enumerate(text.splitlines(), start=1)
        if forbidden in line
    ]


def find_playwright_version_violations(package_json: dict, lockfile: dict) -> list[str]:
    declared = package_json.get("dependencies", {}).get("@playwright/test") or package_json.get(
        "devDependencies", {}
    ).get("@playwright/test")
    locked = lockfile.get("packages", {}).get("node_modules/@playwright/test", {}).get("version")
    violations: list[str] = []
    if declared is None:
        return ["frontend/package.json: @playwright/test is not declared"]
    if not _EXACT_VERSION_RE.match(declared):
        violations.append(
            f"frontend/package.json: @playwright/test must be an exact version, found '{declared}'"
        )
    if locked is None:
        violations.append("frontend/package-lock.json: @playwright/test is not locked")
    elif declared != locked:
        violations.append(
            f"@playwright/test declared '{declared}' differs from lockfile '{locked}'"
        )
    return violations


# --- synthetic cases: prove the checks fail when they must -----------------

_GOOD_WORKFLOW = """name: x
on: push
jobs:
  alpha:
    runs-on: ubuntu-24.04
    steps:
      - run: echo a
  beta:
    runs-on: "ubuntu-24.04"  # pinned
    steps:
      - run: echo b
"""


def test_synthetic_good_workflow_passes():
    assert (
        find_runner_violations(_GOOD_WORKFLOW, "good.yml", require_runs_on_in_every_job=True) == []
    )
    assert find_forbidden_label_lines(_GOOD_WORKFLOW, "good.yml") == []


def test_synthetic_ubuntu_latest_fails():
    text = _GOOD_WORKFLOW.replace(
        "ubuntu-24.04\n    steps:\n      - run: echo a",
        "ubuntu-latest\n    steps:\n      - run: echo a",
    )
    violations = find_runner_violations(text, "bad.yml")
    assert (
        len(violations) == 1 and "ubuntu-latest" in violations[0] and "job=alpha" in violations[0]
    )
    assert find_forbidden_label_lines(text, "bad.yml")


def test_synthetic_other_version_fails():
    text = _GOOD_WORKFLOW.replace("runs-on: ubuntu-24.04\n", "runs-on: ubuntu-26.04\n", 1)
    violations = find_runner_violations(text, "bad.yml")
    assert len(violations) == 1 and "ubuntu-26.04" in violations[0]


def test_synthetic_expression_and_matrix_fail():
    for value in ("${{ matrix.os }}", "${{ inputs.runner }}", "[ubuntu-24.04]", "self-hosted"):
        text = _GOOD_WORKFLOW.replace("runs-on: ubuntu-24.04\n", f"runs-on: {value}\n", 1)
        assert find_runner_violations(text, "bad.yml"), value


def test_synthetic_job_without_runs_on_fails():
    text = _GOOD_WORKFLOW + "  gamma:\n    steps:\n      - run: echo c\n"
    assert find_runner_violations(text, "bad.yml") == []
    violations = find_runner_violations(text, "bad.yml", require_runs_on_in_every_job=True)
    assert violations == ["bad.yml job=gamma: missing runs-on"]


def test_synthetic_playwright_version_cases():
    lock = {"packages": {"node_modules/@playwright/test": {"version": "1.64.1"}}}
    ok = {"devDependencies": {"@playwright/test": "1.64.1"}}
    assert find_playwright_version_violations(ok, lock) == []

    caret = {"devDependencies": {"@playwright/test": "^1.64.1"}}
    caret_violations = find_playwright_version_violations(caret, lock)
    assert any("exact version" in item for item in caret_violations)

    drift = {"devDependencies": {"@playwright/test": "1.64.0"}}
    drift_violations = find_playwright_version_violations(drift, lock)
    assert drift_violations == ["@playwright/test declared '1.64.0' differs from lockfile '1.64.1'"]

    assert find_playwright_version_violations({}, lock) == [
        "frontend/package.json: @playwright/test is not declared"
    ]
    assert find_playwright_version_violations(ok, {}) == [
        "frontend/package-lock.json: @playwright/test is not locked"
    ]


# --- real repository -------------------------------------------------------


def _workflow_files() -> list[Path]:
    return sorted([*WORKFLOWS_DIR.glob("*.yml"), *WORKFLOWS_DIR.glob("*.yaml")])


def test_every_workflow_job_runs_on_the_pinned_runner():
    files = _workflow_files()
    assert CI_WORKFLOW in files
    violations: list[str] = []
    for path in files:
        violations += find_runner_violations(
            path.read_text(encoding="utf-8"),
            str(path.relative_to(ROOT)),
            require_runs_on_in_every_job=path == CI_WORKFLOW,
        )
    assert violations == [], "\n".join(violations)


def test_no_ubuntu_latest_anywhere_under_github_dir():
    violations: list[str] = []
    for path in sorted(p for p in GITHUB_DIR.rglob("*") if p.is_file()):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        violations += find_forbidden_label_lines(text, str(path.relative_to(ROOT)))
    assert violations == [], "\n".join(violations)


def test_ci_workflow_has_jobs_and_all_declare_runs_on():
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    runs_on_count = sum(1 for line in text.splitlines() if _RUNS_ON_RE.match(line))
    job_count = sum(
        1 for line in text.split("\njobs:", 1)[1].splitlines() if _JOB_KEY_RE.match(line)
    )
    assert job_count >= 1
    assert runs_on_count == job_count


def test_playwright_version_is_exact_and_matches_lockfile():
    package_json = json.loads(FRONTEND_PACKAGE.read_text(encoding="utf-8"))
    lockfile = json.loads(FRONTEND_LOCKFILE.read_text(encoding="utf-8"))
    violations = find_playwright_version_violations(package_json, lockfile)
    assert violations == [], "\n".join(violations)
