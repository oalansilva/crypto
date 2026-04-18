from __future__ import annotations

import fnmatch
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_EPHEMERAL_PATTERNS = [
    "frontend/playwright-report/**",
    "frontend/test-results/**",
    "qa_artifacts/**",
    "frontend/qa_artifacts/**",
    "test-results/**",
    ".playwright/**",
    ".pytest_cache/**",
]

ENFORCED_STATUSES = {"Homologation", "Archived"}


class UpstreamGuardError(RuntimeError):
    pass


@dataclass
class UpstreamGuardResult:
    ok: bool
    repo_root: str
    branch: str
    target_statuses: list[str]
    relevant_tracked_changes: list[str]
    relevant_untracked_changes: list[str]
    ignored_ephemeral_changes: list[str]
    unpushed_commits: list[str]
    upstream_ref: str | None

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "repo_root": self.repo_root,
            "branch": self.branch,
            "target_statuses": self.target_statuses,
            "relevant_tracked_changes": self.relevant_tracked_changes,
            "relevant_untracked_changes": self.relevant_untracked_changes,
            "ignored_ephemeral_changes": self.ignored_ephemeral_changes,
            "unpushed_commits": self.unpushed_commits,
            "upstream_ref": self.upstream_ref,
        }

    @property
    def blocking_reasons(self) -> list[str]:
        reasons: list[str] = []
        if self.relevant_tracked_changes:
            reasons.append(
                f"relevant tracked changes: {', '.join(self.relevant_tracked_changes[:10])}"
            )
        if self.relevant_untracked_changes:
            reasons.append(
                f"relevant untracked changes: {', '.join(self.relevant_untracked_changes[:10])}"
            )
        if self.unpushed_commits:
            reasons.append(
                f"unpushed commits against {self.upstream_ref or 'upstream'}: {len(self.unpushed_commits)}"
            )
        return reasons


def _git(repo_root: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise UpstreamGuardError(
            proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed"
        )
    return proc.stdout


def _matches(path: str, patterns: Iterable[str]) -> bool:
    raw_norm = path.strip().lstrip("./")
    norm = raw_norm.rstrip("/")
    is_dir_hint = raw_norm.endswith("/")
    for pat in patterns:
        candidate = pat.strip().lstrip("./").rstrip("/")
        if fnmatch.fnmatch(norm, candidate):
            return True
        if candidate.endswith("/**") and norm == candidate[:-3].rstrip("/"):
            return True
        if is_dir_hint and candidate.startswith(f"{norm}/"):
            return True
    return False


def _extra_patterns() -> list[str]:
    raw = os.getenv("UPSTREAM_GUARD_IGNORE", "")
    return [part.strip() for part in raw.split(":") if part.strip()]


def evaluate_upstream_guard(
    repo_root: str | Path,
    *,
    target_statuses: Iterable[str] | None = None,
    ephemeral_patterns: Iterable[str] | None = None,
) -> UpstreamGuardResult:
    root = Path(repo_root).resolve()
    status_targets = [s for s in (target_statuses or []) if s]
    patterns = list(DEFAULT_EPHEMERAL_PATTERNS)
    if ephemeral_patterns:
        patterns.extend(list(ephemeral_patterns))
    patterns.extend(_extra_patterns())

    branch = _git(root, "branch", "--show-current").strip() or "HEAD"
    tracked_lines = _git(root, "status", "--porcelain").splitlines()
    untracked_lines = _git(root, "ls-files", "--others", "--exclude-standard").splitlines()

    relevant_tracked: list[str] = []
    relevant_untracked: list[str] = []
    ignored_ephemeral: list[str] = []

    seen_untracked = {line.strip() for line in untracked_lines if line.strip()}

    for raw in tracked_lines:
        if not raw.strip():
            continue
        path_part = raw[3:] if len(raw) > 3 else raw
        path = path_part.split(" -> ")[-1].strip()
        if not path:
            continue
        if raw.startswith("??"):
            if _matches(path, patterns):
                ignored_ephemeral.append(path)
            else:
                relevant_untracked.append(path)
            continue
        if path in seen_untracked:
            continue
        if _matches(path, patterns):
            ignored_ephemeral.append(path)
        else:
            relevant_tracked.append(path)

    for path in seen_untracked:
        if _matches(path, patterns):
            ignored_ephemeral.append(path)
        elif path not in relevant_untracked:
            relevant_untracked.append(path)

    upstream_ref = (
        _git(
            root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}", check=False
        ).strip()
        or None
    )
    unpushed_commits: list[str] = []
    if upstream_ref:
        out = _git(root, "log", "--oneline", f"{upstream_ref}..HEAD", check=False).splitlines()
        unpushed_commits = [line.strip() for line in out if line.strip()]
    else:
        unpushed_commits = ["no upstream branch configured for current HEAD"]

    ok = not relevant_tracked and not relevant_untracked and not unpushed_commits
    return UpstreamGuardResult(
        ok=ok,
        repo_root=str(root),
        branch=branch,
        target_statuses=status_targets,
        relevant_tracked_changes=sorted(set(relevant_tracked)),
        relevant_untracked_changes=sorted(set(relevant_untracked)),
        ignored_ephemeral_changes=sorted(set(ignored_ephemeral)),
        unpushed_commits=unpushed_commits,
        upstream_ref=upstream_ref,
    )


def require_upstream_published(
    repo_root: str | Path, *, target_statuses: Iterable[str] | None = None
) -> UpstreamGuardResult:
    result = evaluate_upstream_guard(repo_root, target_statuses=target_statuses)
    if result.ok:
        return result

    targets = (
        ", ".join(result.target_statuses) if result.target_statuses else "workflow progression"
    )
    reasons = "; ".join(result.blocking_reasons) or "unknown upstream guard failure"
    raise UpstreamGuardError(
        f"Upstream guard blocked {targets}. Publish relevant changes to GitHub first ({reasons})."
    )
