from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from t14 import (  # noqa: E402
    CANONICAL_DEV_SOURCE,
    T14Error,
    LiveT14Runner,
    measure_checks_green,
)

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


class Scripted:
    def __init__(self, responses: list[subprocess.CompletedProcess[str]]) -> None:
        self.responses = list(responses)
        self.calls: list[list[str]] = []

    def __call__(self, args, **kwargs):  # noqa: ANN001
        self.calls.append(list(args))
        if not self.responses:
            raise AssertionError(f"unexpected call {args}")
        return self.responses.pop(0)


def _ok(stdout: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_measure_checks_green_qa_gate_pass():
    scripted = Scripted(
        [
            _ok(json.dumps([{"number": 99, "headRefOid": "abc"}])),
            _ok(json.dumps([{"name": "qa-gate", "state": "SUCCESS"}, {"name": "other", "state": "FAILURE"}])),
        ]
    )
    assert measure_checks_green("632", "card-632-t14-live-done", runner=scripted) is True


def test_measure_checks_green_ignores_gh_checks_exit_code():
    scripted = Scripted(
        [
            _ok(json.dumps([{"number": 99, "headRefOid": "abc"}])),
            _ok(
                json.dumps([{"name": "qa-gate", "state": "SUCCESS"}, {"name": "other", "state": "FAILURE"}]),
                returncode=1,
            ),
        ]
    )
    assert measure_checks_green("632", "card-632-t14-live-done", runner=scripted) is True


def test_measure_checks_green_missing_or_fail():
    empty = Scripted([_ok("[]")])
    assert measure_checks_green("632", "card-632-x", runner=empty) is False
    failed = Scripted(
        [
            _ok(json.dumps([{"number": 1, "headRefOid": "abc"}])),
            _ok(json.dumps([{"name": "qa-gate", "state": "FAILURE"}])),
        ]
    )
    assert measure_checks_green("632", "card-632-x", runner=failed) is False
    missing = Scripted(
        [
            _ok(json.dumps([{"number": 1, "headRefOid": "abc"}])),
            _ok(json.dumps([{"name": "lint", "state": "SUCCESS"}])),
        ]
    )
    assert measure_checks_green("632", "card-632-x", runner=missing) is False


def test_measure_checks_green_error_is_false():
    boom = Scripted([_ok("{not-json")])
    assert measure_checks_green("632", "card-632-x", runner=boom) is False


def _git(args: list[str], cwd: Path) -> None:
    proc = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    assert proc.returncode == 0


def test_sync_dirty_raises_before_mutate(tmp_path: Path):
    _git(["git", "init"], tmp_path)
    _git(["git", "config", "user.email", "t14@test"], tmp_path)
    _git(["git", "config", "user.name", "t14"], tmp_path)
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    _git(["git", "add", "a.txt"], tmp_path)
    _git(["git", "commit", "-m", "init"], tmp_path)
    (tmp_path / "dirt.txt").write_text("nope\n", encoding="utf-8")
    calls: list[list[str]] = []

    def wrapped(args, **kwargs):  # noqa: ANN001
        calls.append(list(args))
        return subprocess.run(args, **kwargs)

    runner = LiveT14Runner(source=tmp_path, restart_path=tmp_path / "restart", runner=wrapped)
    with pytest.raises(T14Error, match="dirty"):
        runner.sync_dev_source()
    assert any("--porcelain" in c for c in calls)
    assert not any("reset" in c for c in calls)
    assert not any(len(c) >= 4 and c[3] == "merge" for c in calls)
    assert not any(len(c) >= 4 and c[3] == "checkout" for c in calls)


def test_restart_rejects_noncanonical_path_on_canonical_source(tmp_path: Path):
    runner = LiveT14Runner(source=CANONICAL_DEV_SOURCE, restart_path=tmp_path / "restart")
    with pytest.raises(T14Error, match="path"):
        runner.restart()
