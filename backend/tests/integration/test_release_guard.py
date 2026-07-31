from __future__ import annotations

import subprocess
from pathlib import Path

RELEASE_GUARD = Path(__file__).resolve().parents[3] / "scripts" / "release-guard"


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
    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "branch", "develop")
    _git(repo, "push", "-u", "origin", "main", "develop")
    return repo


def _run_post_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(RELEASE_GUARD), "post"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def _commit_file(repo: Path, relative_path: str, content: str, message: str) -> None:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", relative_path)
    _git(repo, "commit", "-m", message)


def test_post_release_allows_identical_remote_commits(tmp_path: Path):
    repo = _init_repo(tmp_path)

    result = _run_post_guard(repo)

    assert result.returncode == 0
    assert "same commit" in result.stdout
    assert "Result: PASS" in result.stdout


def test_post_release_allows_main_merge_commit_with_identical_tree(tmp_path: Path):
    repo = _init_repo(tmp_path)
    _git(repo, "switch", "develop")
    _commit_file(repo, "release.txt", "included\n", "release content")
    _git(repo, "push", "origin", "develop")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "develop", "-m", "merge develop")
    _git(repo, "push", "origin", "main")

    result = _run_post_guard(repo)

    assert result.returncode == 0
    assert "ancestor of origin/main with identical trees" in result.stdout
    assert "Result: PASS" in result.stdout


def test_post_release_blocks_material_tree_divergence(tmp_path: Path):
    repo = _init_repo(tmp_path)
    _git(repo, "switch", "develop")
    _commit_file(repo, "release.txt", "included\n", "release content")
    _git(repo, "push", "origin", "develop")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "develop", "-m", "merge develop")
    _commit_file(repo, "main-only.txt", "drift\n", "main-only drift")
    _git(repo, "push", "origin", "main")

    result = _run_post_guard(repo)

    assert result.returncode == 1
    assert "identical content trees" in result.stdout
    assert "Result: FAIL" in result.stdout


def test_post_release_blocks_identical_trees_without_develop_ancestry(tmp_path: Path):
    repo = _init_repo(tmp_path)
    _git(repo, "switch", "develop")
    _git(repo, "commit", "--allow-empty", "-m", "develop-only history")
    _git(repo, "push", "origin", "develop")
    _git(repo, "switch", "main")
    _git(repo, "commit", "--allow-empty", "-m", "main-only history")
    _git(repo, "push", "origin", "main")

    result = _run_post_guard(repo)

    assert result.returncode == 1
    assert "origin/develop to equal or be an ancestor of origin/main" in result.stdout
    assert "Result: FAIL" in result.stdout
