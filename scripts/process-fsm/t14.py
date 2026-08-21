"""T14 live measurer and atomic closeout runner. Tests inject fakes; no GitHub in pytest."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Protocol

CANONICAL_DEV_SOURCE = Path("/srv/apps/dev/criptofarol/source")
CANONICAL_RESTART = CANONICAL_DEV_SOURCE / "restart"
DEV_PUBLIC_HEALTH = "https://dev.criptofarol.com.br/api/health"
GH_REPO = "oalansilva/crypto"
QA_GATE = "qa-gate"
HEALTH_ATTEMPTS = 15
HEALTH_SLEEP_S = 1
_GIT_OVERRIDE_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_COMMON_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


class T14Error(RuntimeError):
    """I8: squash/sync/restart/comment failed. Status stays QA."""


class T14Runner(Protocol):
    def squash(self, *, q_git: str, bound_card: str) -> None: ...

    def sync_dev_source(self) -> None: ...

    def restart(self) -> None: ...

    def comment_done(self, *, bound_card: str, q_git: str) -> None: ...


class RecordingT14Runner:
    def __init__(self, fail_at: str | None = None) -> None:
        self.calls: list[str] = []
        self.fail_at = fail_at

    def _step(self, name: str) -> None:
        self.calls.append(name)
        if self.fail_at == name:
            raise T14Error(name)

    def squash(self, *, q_git: str, bound_card: str) -> None:
        self._step("squash")

    def sync_dev_source(self) -> None:
        self._step("sync_dev_source")

    def restart(self) -> None:
        self._step("restart")

    def comment_done(self, *, bound_card: str, q_git: str) -> None:
        self._step("comment_done")


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in _GIT_OVERRIDE_VARS:
        env.pop(key, None)
    return env


def _run(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    return runner(
        args,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        env=_git_env(),
    )


def _pr_list_json(
    q_git: str,
    *,
    fields: str,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[dict]:
    """List PRs for branch head. gh 2.45 matches --head by branch name, not owner:branch."""
    listed = _run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            GH_REPO,
            "--head",
            str(q_git),
            "--base",
            "develop",
            "--state",
            "all",
            "--limit",
            "1",
            "--json",
            fields,
        ],
        timeout=20,
        runner=runner,
    )
    if listed.returncode != 0:
        return []
    rows = json.loads(listed.stdout or "[]")
    return rows if isinstance(rows, list) else []


def measure_checks_green(
    bound_card: str | int | None,
    q_git: str | None,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> bool:
    del bound_card
    if not q_git:
        return False
    try:
        rows = _pr_list_json(str(q_git), fields="number,headRefOid", runner=runner)
        if not rows:
            return False
        head = rows[0].get("headRefOid")
        if not head:
            return False
        # gh 2.45 has no `pr checks --json`; use Checks API on the head SHA.
        checks = _run(
            [
                "gh",
                "api",
                f"repos/{GH_REPO}/commits/{head}/check-runs",
                "--paginate",
                "--jq",
                ".check_runs[] | {name,status,conclusion}",
            ],
            timeout=30,
            runner=runner,
        )
        if checks.returncode != 0:
            return False
        text = (checks.stdout or "").strip()
        if not text:
            return False
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(item.get("name") or "") != QA_GATE:
                continue
            status = str(item.get("status") or "").lower()
            conclusion = str(item.get("conclusion") or "").lower()
            return status == "completed" and conclusion == "success"
        return False
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, TypeError, ValueError):
        return False


class LiveT14Runner:
    def __init__(
        self,
        *,
        source: Path = CANONICAL_DEV_SOURCE,
        restart_path: Path = CANONICAL_RESTART,
        health_url: str = DEV_PUBLIC_HEALTH,
        comment_script: Path | None = None,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        health_get: Callable[[str], bool] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.source = source
        self.restart_path = restart_path
        self.health_url = health_url
        self.comment_script = comment_script or (CANONICAL_DEV_SOURCE / "scripts" / "post-card-evidence-comment.sh")
        self._run = runner
        self._health_get = health_get or _http_health
        self._sleep = sleep
        self.commit = ""
        self.pr: str | None = None

    def squash(self, *, q_git: str, bound_card: str) -> None:
        del bound_card
        try:
            rows = _pr_list_json(str(q_git), fields="number,state,mergedAt", runner=self._run)
        except json.JSONDecodeError as exc:
            raise T14Error("squash: pr list json") from exc
        if not rows:
            if self._sha_on_develop(q_git):
                return
            raise T14Error("squash: no PR")
        number = rows[0].get("number")
        state = str(rows[0].get("state") or "").upper()
        merged = rows[0].get("mergedAt")
        if number is None:
            raise T14Error("squash: no PR number")
        self.pr = str(number)
        if state == "MERGED" or merged:
            return
        merged_pr = _run(
            [
                "gh",
                "pr",
                "merge",
                str(number),
                "--repo",
                GH_REPO,
                "--squash",
            ],
            timeout=120,
            runner=self._run,
        )
        if merged_pr.returncode != 0:
            raise T14Error((merged_pr.stderr or merged_pr.stdout or "squash merge failed").strip())

    def _sha_on_develop(self, q_git: str) -> bool:
        fetch = _run(["git", "-C", str(self.source), "fetch", "origin", q_git, "develop"], timeout=60, runner=self._run)
        if fetch.returncode != 0:
            return False
        ancestor = _run(
            ["git", "-C", str(self.source), "merge-base", "--is-ancestor", f"origin/{q_git}", "origin/develop"],
            timeout=20,
            runner=self._run,
        )
        return ancestor.returncode == 0

    def sync_dev_source(self) -> None:
        porcelain = _run(
            ["git", "-C", str(self.source), "status", "--porcelain"],
            timeout=20,
            runner=self._run,
        )
        if porcelain.returncode != 0:
            raise T14Error("sync: status failed")
        if (porcelain.stdout or "").strip():
            raise T14Error("sync: dirty")
        for args, label in (
            (["git", "-C", str(self.source), "fetch", "origin"], "fetch"),
            (["git", "-C", str(self.source), "checkout", "develop"], "checkout"),
            (["git", "-C", str(self.source), "merge", "--ff-only", "origin/develop"], "ff-only"),
        ):
            proc = _run(args, timeout=120, runner=self._run)
            if proc.returncode != 0:
                raise T14Error(f"sync: {label}")
        sha = _run(
            ["git", "-C", str(self.source), "rev-parse", "HEAD"],
            timeout=20,
            runner=self._run,
        )
        if sha.returncode != 0 or not (sha.stdout or "").strip():
            raise T14Error("sync: rev-parse")
        self.commit = (sha.stdout or "").strip()

    def restart(self) -> None:
        restart = Path(self.restart_path)
        if self.source == CANONICAL_DEV_SOURCE and restart != CANONICAL_RESTART:
            raise T14Error("restart: path")
        proc = _run([str(restart)], timeout=600, runner=self._run)
        if proc.returncode != 0:
            raise T14Error((proc.stderr or proc.stdout or "restart failed").strip())
        for _ in range(HEALTH_ATTEMPTS):
            if self._health_get(self.health_url):
                return
            self._sleep(HEALTH_SLEEP_S)
        raise T14Error("restart: public health")

    def comment_done(self, *, bound_card: str, q_git: str) -> None:
        del q_git
        if not self.commit:
            raise T14Error("comment_done: no commit")
        script = self.comment_script
        args = [
            "bash",
            str(script),
            "--transition",
            "done",
            "--card",
            str(bound_card),
            "--commit",
            self.commit,
            "--branch",
            "develop",
            "--review",
            "qa-gate green; canonical DEV restart; public health 200",
        ]
        if self.pr:
            args.extend(["--pr", self.pr])
        proc = _run(args, timeout=60, runner=self._run)
        if proc.returncode != 0:
            raise T14Error((proc.stderr or proc.stdout or "comment_done failed").strip())


def _http_health(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            return int(getattr(resp, "status", 0) or 0) == 200
    except (OSError, urllib.error.URLError, ValueError):
        return False


def run_t14(runner: T14Runner, *, q_git: str, bound_card: str) -> None:
    try:
        runner.squash(q_git=q_git, bound_card=bound_card)
        runner.sync_dev_source()
        runner.restart()
        runner.comment_done(bound_card=bound_card, q_git=q_git)
    except T14Error:
        raise
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise T14Error(str(exc)) from exc
