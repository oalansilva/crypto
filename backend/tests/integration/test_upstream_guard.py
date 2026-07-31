from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from app.services.upstream_guard import (
    UpstreamGuardError,
    evaluate_upstream_guard,
    require_card_main_publication,
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _init_repo(tmp_path: Path) -> Path:
    bare = tmp_path / "remote.git"
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True, text=True)
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True)
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "remote", "add", "origin", str(bare))
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    _git(repo, "branch", "-M", "main")
    _git(repo, "push", "-u", "origin", "main")
    return repo


def test_upstream_guard_allows_clean_repo_with_upstream(tmp_path: Path):
    repo = _init_repo(tmp_path)

    result = evaluate_upstream_guard(repo, target_statuses=["QA"])

    assert result.ok is True
    assert result.upstream_ref == "origin/main"
    assert result.relevant_tracked_changes == []
    assert result.relevant_untracked_changes == []
    assert result.unpushed_commits == []


def test_upstream_guard_ignores_ephemeral_qa_artifacts(tmp_path: Path):
    repo = _init_repo(tmp_path)
    out = repo / "frontend" / "playwright-report"
    out.mkdir(parents=True)
    (out / "index.html").write_text("report\n", encoding="utf-8")

    result = evaluate_upstream_guard(repo, target_statuses=["Homologation"])

    assert result.ok is True
    assert "frontend/playwright-report/index.html" in result.ignored_ephemeral_changes


def test_upstream_guard_blocks_relevant_changes_and_unpushed_commits(tmp_path: Path):
    repo = _init_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src" / "feature.ts").write_text("export const x = 1;\n", encoding="utf-8")
    _git(repo, "add", "src/feature.ts")
    _git(repo, "commit", "-m", "feature")
    (repo / "notes.txt").write_text("still local\n", encoding="utf-8")

    result = evaluate_upstream_guard(repo, target_statuses=["Archived"])

    assert result.ok is False
    assert result.unpushed_commits
    assert "notes.txt" in result.relevant_untracked_changes


def test_card_publication_is_found_in_main_independently_of_checkout(tmp_path: Path):
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("published card\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "feat: concluir card-340-design-approval-kanban-flow (#340)")
    published_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()
    _git(repo, "push", "origin", "main")

    _git(repo, "switch", "-c", "develop")
    (repo / "README.md").write_text("develop moved on\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "feat: unrelated develop work")

    evidence = require_card_main_publication(
        repo,
        change_id="card-340-design-approval-kanban-flow",
        card_number=999,
    )
    assert evidence.head_sha == published_sha
    assert evidence.main_ref == "origin/main"


def test_card_publication_rejects_unpublished_card_reference(tmp_path: Path):
    repo = _init_repo(tmp_path)
    with pytest.raises(UpstreamGuardError, match="No commit"):
        require_card_main_publication(
            repo,
            change_id="card-340-design-approval-kanban-flow",
            card_number=340,
        )


def test_card_publication_accepts_explicit_number_for_slug_change_id(tmp_path: Path):
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("published manual card\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "feat: concluir fluxo manual (#340)")
    published_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()
    _git(repo, "push", "origin", "main")

    evidence = require_card_main_publication(
        repo,
        change_id="design-approval-kanban-flow",
        card_number=340,
    )
    assert evidence.head_sha == published_sha
