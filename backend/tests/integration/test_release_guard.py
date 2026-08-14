from __future__ import annotations

import os
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
    release_dir = repo / "docs"
    release_dir.mkdir()
    (release_dir / "release-2026-01-01.md").write_text(
        "# Release 2026-01-01\n\nRelease de teste commitada sem placeholders.\n",
        encoding="utf-8",
    )
    _git(repo, "add", "README.md", "docs/release-2026-01-01.md")
    _git(repo, "commit", "-m", "initial")
    _git(repo, "branch", "-M", "main")
    _git(repo, "branch", "develop")
    _git(repo, "push", "-u", "origin", "main", "develop")
    return repo


def _run_guard(
    repo: Path,
    mode: str = "post",
    *,
    release_cards: str | None = None,
    fake_gh: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PROD_DEPLOY_EVIDENCE"] = "test-commit services=app url=https://example.com"
    if release_cards is not None:
        env["RELEASE_CARDS"] = release_cards
    else:
        env.pop("RELEASE_CARDS", None)
    if fake_gh is not None:
        env["PATH"] = f"{fake_gh.parent}:{env['PATH']}"
    return subprocess.run(
        [str(RELEASE_GUARD), mode],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def _run_post_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return _run_guard(repo)


def _fake_gh(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "gh"
    script.write_text(
        """#!/usr/bin/env bash
set -u
case "${1:-} ${2:-}" in
  "auth status") exit 0 ;;
  "project item-list")
    printf '%s\\n' "${FAKE_BOARD_JSON:?}"
    [[ "${FAKE_FAIL_PROJECT:-}" == "1" ]] && exit 1
    exit 0
    ;;
  "pr list") printf '[]\\n' ;;
  "api repos/oalansilva/crypto/issues/"*)
    card="${2#repos/oalansilva/crypto/issues/}"
    card="${card%/comments}"
    [[ "${FAKE_FAIL_CARD:-}" == "$card" ]] && exit 1
    printf '%s\\n' "${FAKE_COMMENTS:-}"
    ;;
  *) printf 'unexpected gh call: %s\\n' "$*" >&2; exit 1 ;;
esac
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _board(*cards: tuple[int, str]) -> str:
    items = ",".join(
        f'{{"content":{{"number":{number}}},"status":"{status}",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}'
        for number, status in cards
    )
    return f'{{"items":[{items}]}}'


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


def test_post_blocks_missing_homologation_comment(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_COMMENTS", "Outro comentário")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "BLOCKER: card #480 is Pronto without canonical homologation comment" in result.stdout


def test_audit_warns_for_missing_homologation_comment(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Homologado")))
    monkeypatch.setenv("FAKE_COMMENTS", "Outro comentário")

    result = _run_guard(repo, "audit", release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "WARN: card #480 is Homologado without canonical homologation comment" in result.stdout


def test_post_accepts_comment_and_deduplicates_release_cards(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    result = _run_guard(repo, release_cards="480, 0480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert result.stdout.count("Card #480 has canonical homologation evidence.") == 1


def test_post_blocks_invalid_release_card_id(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, release_cards="480,nope", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "RELEASE_CARDS contains invalid card identifiers" in result.stdout


def test_post_blocks_card_id_with_internal_whitespace(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, release_cards="4 80", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "RELEASE_CARDS contains invalid card identifiers" in result.stdout


def test_post_blocks_overflowing_release_card_id(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, release_cards="18446744073709552096", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "out-of-range card identifier" in result.stdout
    assert "Card #480 has canonical homologation evidence" not in result.stdout


def test_post_blocks_when_comment_query_fails(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_FAIL_CARD", "480")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "could not list all comments for card #480" in result.stdout


def test_post_blocks_when_project_query_fails_with_valid_json(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_FAIL_PROJECT", "1")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "gh project item-list failed" in result.stdout


def test_post_warns_and_skips_without_release_cards(tmp_path: Path):
    repo = _init_repo(tmp_path)

    result = _run_guard(repo)

    assert result.returncode == 0
    assert "RELEASE_CARDS not set; package homologation-comment check skipped" in result.stdout
