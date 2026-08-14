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
LOG="${GH_CALL_LOG:-}"
[[ -n "$LOG" ]] && printf 'CALL %s\\n' "$*" >> "$LOG"
case "${1:-} ${2:-}" in
  "auth status") exit 0 ;;
  "project item-list")
    printf '%s\\n' "${FAKE_BOARD_JSON:?}"
    [[ "${FAKE_FAIL_PROJECT:-}" == "1" ]] && exit 1
    exit 0
    ;;
  "pr list") printf '%s\\n' "${FAKE_PR_JSON:-[]}" ;;
  "api rate_limit")
    [[ "${FAKE_FAIL_RATE_LIMIT:-}" == "1" ]] && exit 1
    printf '%s\\n' '{"resources":{"graphql":{"limit":5000,"used":123,"remaining":4877,"reset":1786673805}}}'
    ;;
  "api graphql")
    count="$(grep -c 'CALL api graphql' "$LOG" 2>/dev/null || true)"
    count="${count:-0}"
    if [[ "$count" -ge 20 ]]; then
      printf '%s\\n' '{"data":{"node":{"items":{"pageInfo":{"hasNextPage":false},"nodes":[]}}}}'
    else
      printf '%s\\n' '{"data":{"node":{"items":{"pageInfo":{"hasNextPage":true,"endCursor":"c1"},"nodes":[{"updatedAt":"2026-08-14T00:00:00Z","content":{"number":1,"title":"x"},"fieldValueByName":{"name":"Todo"}}]}}}}'
    fi
    ;;
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


def _board(*cards: tuple, repository: str = "oalansilva/crypto") -> str:
    def _item(card: tuple) -> str:
        number, status = card[0], card[1]
        title = card[2] if len(card) > 2 else f"Card {number}"
        return (
            f'{{"content":{{"number":{number},"repository":"{repository}","title":"{title}"}},'
            f'"status":"{status}","responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}}'
        )

    items = ",".join(_item(card) for card in cards)
    return f'{{"items":[{items}],"totalCount":{len(cards)}}}'


def _call_count(log: Path, needle: str) -> int:
    if not log.exists():
        return 0
    return sum(1 for line in log.read_text(encoding="utf-8").splitlines() if needle in line)


def _commit_file(repo: Path, relative_path: str, content: str, message: str) -> None:
    path = repo / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", relative_path)
    _git(repo, "commit", "-m", message)


def _make_branches(repo: Path, *names: str) -> None:
    _git(repo, "switch", "develop")
    for name in names:
        _commit_file(repo, f"{name}.txt", f"{name}\n", f"branch {name}")
        _git(repo, "branch", name)
    _git(repo, "push", "origin", "develop")


def _make_change(
    repo: Path, change_name: str, *, complete: bool = True, proposal: str = ""
) -> None:
    """Cria uma change OpenSpec ativa (complete ou in-progress) no repo."""
    base = repo / "openspec" / "changes" / change_name
    (base / "specs" / "alpha").mkdir(parents=True)
    (base / "proposal.md").write_text(
        proposal or f"# {change_name}\n\nChange de teste.\n", encoding="utf-8"
    )
    (base / "design.md").write_text(f"# Design {change_name}\n", encoding="utf-8")
    if complete:
        (base / "tasks.md").write_text("- [x] 1.1 Tarefa concluída\n", encoding="utf-8")
    else:
        (base / "tasks.md").write_text(
            "- [x] 1.1 Tarefa concluída\n- [ ] 1.2 Tarefa pendente\n", encoding="utf-8"
        )
    (base / "specs" / "alpha" / "spec.md").write_text(
        "## ADDED Requirements\n\n### Requirement: alpha\n\n#### Scenario: alpha\n- **WHEN** x\n- **THEN** y\n",
        encoding="utf-8",
    )
    _git(repo, "add", f"openspec/changes/{change_name}")
    _git(repo, "commit", "-m", f"add change {change_name}")


def _remove_change(repo: Path, change_name: str) -> None:
    _git(repo, "rm", "-r", f"openspec/changes/{change_name}")
    _git(repo, "commit", "-m", f"remove change {change_name}")


def test_post_release_allows_identical_remote_commits(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board())
    monkeypatch.setenv("FAKE_PR_JSON", "[]")

    result = _run_guard(repo, fake_gh=fake_gh)

    assert result.returncode == 0
    assert "same commit" in result.stdout
    assert "Result: PASS" in result.stdout


def test_post_release_allows_main_merge_commit_with_identical_tree(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board())
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    _git(repo, "switch", "develop")
    _commit_file(repo, "release.txt", "included\n", "release content")
    _git(repo, "push", "origin", "develop")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "develop", "-m", "merge develop")
    _git(repo, "push", "origin", "main")

    result = _run_guard(repo, fake_gh=fake_gh)

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


def test_post_warns_and_skips_without_release_cards(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board())
    monkeypatch.setenv("FAKE_PR_JSON", "[]")

    result = _run_guard(repo, fake_gh=fake_gh)

    assert result.returncode == 0
    assert "RELEASE_CARDS not set; package homologation-comment check skipped" in result.stdout


def test_audit_single_board_and_pr_snapshot_with_many_branches(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a", "card-200-b")
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv(
        "FAKE_BOARD_JSON", _board((100, "Pronto"), (200, "Cancelado"), (480, "Pronto"))
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    result = _run_guard(repo, "audit", release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert _call_count(call_log, "CALL project item-list") == 1
    assert _call_count(call_log, "CALL pr list") == 1
    assert "Card #480 has canonical homologation evidence." in result.stdout


def test_second_run_refetches_snapshots(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    _run_guard(repo, release_cards="480", fake_gh=fake_gh)
    _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert _call_count(call_log, "CALL project item-list") == 2


def test_post_blocks_truncated_board_snapshot(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        '{"items":[{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"Pronto",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}],"totalCount":2}',
    )

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "incomplete snapshot" in result.stdout


def test_post_blocks_missing_package_card(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((470, "Pronto")))

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "missing, duplicated, or without Status" in result.stdout


def test_post_blocks_package_card_without_status(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        '{"items":[{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}],"totalCount":1}',
    )

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "without Status" in result.stdout


def test_post_blocks_truncated_pr_snapshot(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    prs = ",".join(
        f'{{"number":{i},"headRefName":"b{i}","headRepositoryOwner":{{"login":"oalansilva"}}}}'
        for i in range(1000)
    )
    monkeypatch.setenv("FAKE_PR_JSON", f"[{prs}]")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "1000-item limit" in result.stdout


def test_post_blocks_snapshot_failure_without_consumers(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board())
    monkeypatch.setenv("FAKE_FAIL_PROJECT", "1")

    result = _run_guard(repo, fake_gh=fake_gh)

    assert result.returncode == 1
    assert "board snapshot failed or invalid" in result.stdout


def test_same_snapshot_failure_post_blocker_audit_warning(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board())
    monkeypatch.setenv("FAKE_FAIL_PROJECT", "1")

    post = _run_guard(repo, fake_gh=fake_gh)
    audit = _run_guard(repo, "audit", fake_gh=fake_gh)

    assert post.returncode == 1
    assert "BLOCKER: board snapshot failed or invalid" in post.stdout
    assert audit.returncode == 0
    assert "WARN: board snapshot failed or invalid" in audit.stdout


def test_release_cards_normalization_dedupes_and_single_remote_call(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    result = _run_guard(repo, release_cards=" 480, 0480 ", fake_gh=fake_gh)

    assert result.returncode == 0
    assert result.stdout.count("Card #480 has canonical homologation evidence.") == 1
    assert _call_count(call_log, "CALL project item-list") == 1
    assert _call_count(call_log, "CALL api repos/oalansilva/crypto/issues/480/comments") == 1


def test_invalid_release_card_blocks_before_remote_calls(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, release_cards="480,nope", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "RELEASE_CARDS contains invalid card identifiers" in result.stdout
    assert _call_count(call_log, "CALL project item-list") == 0
    assert _call_count(call_log, "CALL pr list") == 0


def test_audit_age_inventory_caps_at_19_pages(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, "audit", release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert _call_count(call_log, "CALL api graphql") == 19
    assert "truncated at 19 GraphQL pages" in result.stdout


def test_package_card_matched_by_repository_identity(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    items = ",".join(
        [
            '{"content":{"number":480,"repository":"oalansilva/other"},"status":"Pronto",'
            '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}',
            '{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"Pronto",'
            '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}',
        ]
    )
    monkeypatch.setenv("FAKE_BOARD_JSON", f'{{"items":[{items}],"totalCount":2}}')
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "Board fields present for RELEASE_CARDS package." in result.stdout
    assert result.stdout.count("Card #480 has canonical homologation evidence.") == 1


def test_pr_owner_qualified_lookup(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((100, "Pronto")))
    monkeypatch.setenv(
        "FAKE_PR_JSON",
        '[{"number":1,"headRefName":"change-100-a","headRepositoryOwner":{"login":"other-user"}}]',
    )

    result = _run_guard(repo, "audit", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "pr_open=no" in result.stdout


def test_pr_snapshot_failure_never_reports_pr_open_no(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((100, "Pronto")))
    monkeypatch.setenv("FAKE_PR_JSON", "{}")

    result = _run_guard(repo, "audit", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "prs snapshot failed or invalid" in result.stdout
    assert "pr_open=unknown" in result.stdout


def test_rate_limit_diagnostic_absent_on_success_and_once_on_failure(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv("FAKE_COMMENTS", "Homologado por Alan na develop.")

    ok = _run_guard(repo, release_cards="480", fake_gh=fake_gh)
    assert ok.returncode == 0
    assert _call_count(call_log, "CALL api rate_limit") == 0

    monkeypatch.setenv("FAKE_FAIL_PROJECT", "1")
    failed = _run_guard(repo, release_cards="480", fake_gh=fake_gh)
    assert failed.returncode == 1
    assert _call_count(call_log, "CALL api rate_limit") == 1
    assert "rate-limit diagnostic" in failed.stdout


def test_pr_open_yes_positive_match(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((100, "Pronto")))
    monkeypatch.setenv(
        "FAKE_PR_JSON",
        '[{"number":1,"headRefName":"change-100-a","headRepositoryOwner":{"login":"oalansilva"}}]',
    )

    result = _run_guard(repo, "audit", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "pr_open=yes" in result.stdout


def test_pre_mode_performs_no_board_or_pr_queries(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, "pre", fake_gh=fake_gh)

    assert _call_count(call_log, "CALL project item-list") == 0
    assert _call_count(call_log, "CALL pr list") == 0
    assert _call_count(call_log, "CALL api graphql") == 0


def test_audit_invalid_release_cards_warns_and_runs_independent_checks(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))

    result = _run_guard(repo, "audit", release_cards="480,nope", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "WARN: RELEASE_CARDS contains invalid card identifiers" in result.stdout
    assert "RELEASE_CARDS invalid; package homologation-comment check skipped" in result.stdout


def test_post_blocks_duplicate_package_card(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    dup = (
        '{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"Pronto",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}'
    )
    monkeypatch.setenv("FAKE_BOARD_JSON", f'{{"items":[{dup},{dup}],"totalCount":2}}')

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "found 2 matching items" in result.stdout


def test_post_blocks_pr_entries_missing_identity(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Pronto")))
    monkeypatch.setenv(
        "FAKE_PR_JSON",
        '[{"number":1,"headRefName":"","headRepositoryOwner":{"login":"oalansilva"}}]',
    )

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "missing headRefName or headRepositoryOwner.login" in result.stdout


def test_post_blocks_board_without_total_count(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        '{"items":[{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"Pronto",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}]}',
    )

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "incomplete snapshot" in result.stdout


def test_post_blocks_board_items_exceeding_total_count(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        '{"items":[{"content":{"number":480,"repository":"oalansilva/crypto"},"status":"Pronto",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"},'
        '{"content":{"number":481,"repository":"oalansilva/crypto"},"status":"Pronto",'
        '"responsavel":"Codex","prioridade":"P1","tipo":"Operacao"}],"totalCount":1}',
    )

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "incomplete snapshot" in result.stdout


def test_post_blocks_unparseable_board_json(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", "not-json")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "board snapshot failed or invalid" in result.stdout


def test_post_blocks_branch_card_with_unknown_status(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((200, "Pronto")))
    monkeypatch.setenv("FAKE_PR_JSON", "[]")

    result = _run_guard(repo, fake_gh=fake_gh)

    assert result.returncode == 1
    assert "could not determine terminal status for card #100" in result.stdout


def test_audit_branch_card_non_terminal_is_preserved(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_branches(repo, "change-100-a")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((100, "Em desenvolvimento")))
    monkeypatch.setenv("FAKE_PR_JSON", "[]")

    result = _run_guard(repo, "audit", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "card in flight" in result.stdout


def test_post_known_non_eligible_status_keeps_not_applicable(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board((480, "Todo")))
    monkeypatch.setenv("FAKE_COMMENTS", "")

    result = _run_guard(repo, release_cards="480", fake_gh=fake_gh)

    assert result.returncode == 0
    assert "homologation-comment check not applicable" in result.stdout


# --- Card #517: OpenSpec terminal changes check ---


def _audit_with_terminal_changes(
    tmp_path: Path, monkeypatch, *, changes, board_cards, release_cards
):
    repo = _init_repo(tmp_path)
    for change in changes:
        _make_change(repo, change[0], complete=change[1], proposal=change[2] or "")
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv("FAKE_BOARD_JSON", _board(*board_cards))
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    result = _run_guard(repo, "audit", release_cards=release_cards, fake_gh=fake_gh)
    return result


def test_audit_flags_complete_changes_without_id_mapped_by_title(tmp_path: Path, monkeypatch):
    changes = [
        (
            "walk-forward-gate",
            True,
            "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout",
        ),
        (
            "kaizen-stuck-cards-age-alert",
            True,
            "Alerta de cards presos por idade nas colunas do board",
        ),
    ]
    board_cards = [
        (
            470,
            "Pronto",
            "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout",
        ),
        (481, "Pronto", "Kaizen: alerta de cards presos por idade nas colunas do board"),
    ]
    result = _audit_with_terminal_changes(
        tmp_path, monkeypatch, changes=changes, board_cards=board_cards, release_cards="470,481"
    )

    assert result.returncode == 0
    assert "OpenSpec change of terminal card is still active" in result.stdout
    assert "walk-forward-gate" in result.stdout
    assert "card #470" in result.stdout
    assert "kaizen-stuck-cards-age-alert" in result.stdout
    assert "card #481" in result.stdout
    assert "progress=complete" in result.stdout
    assert "mapping=title" in result.stdout


def test_audit_flags_in_progress_change_with_id_on_terminal_card(tmp_path: Path, monkeypatch):
    changes = [("card-509-release-guard-graphql-budget", False, "")]
    board_cards = [(509, "Pronto", "bug: rate limit GraphQL no closeout do release guard")]
    result = _audit_with_terminal_changes(
        tmp_path, monkeypatch, changes=changes, board_cards=board_cards, release_cards="509"
    )

    assert result.returncode == 0
    assert "OpenSpec change of terminal card is still active" in result.stdout
    assert "card-509-release-guard-graphql-budget" in result.stdout
    assert "card #509" in result.stdout
    assert "progress=in-progress" in result.stdout
    assert "mapping=name" in result.stdout


def test_post_blocks_complete_change_by_name_and_in_progress_by_title(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_change(repo, "card-480-kaizen-evidence", complete=True)
    _make_change(
        repo,
        "hide-quant-test-templates",
        complete=False,
        proposal="Excluir templates de teste quantitativos do catálogo de estratégias visíveis",
    )
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        _board(
            (480, "Pronto", "Kaizen: comentário de evidência de homologação no card"),
            (489, "Pronto", "Excluir templates de teste quantitativos do catálogo de estratégias"),
        ),
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    result = _run_guard(repo, release_cards="480,489", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "card-480-kaizen-evidence" in result.stdout
    assert "card #480" in result.stdout
    assert "mapping=name" in result.stdout
    assert "hide-quant-test-templates" in result.stdout
    assert "card #489" in result.stdout
    assert "mapping=title" in result.stdout
    assert "package=yes" in result.stdout
    assert "Result: FAIL" in result.stdout


def test_post_blocks_without_release_cards_when_global_terminal_change_exists(
    tmp_path: Path, monkeypatch
):
    repo = _init_repo(tmp_path)
    _make_change(repo, "walk-forward-gate", complete=True)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        _board(
            (
                470,
                "Pronto",
                "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout",
            )
        ),
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    result = _run_guard(repo, fake_gh=fake_gh)

    assert result.returncode == 1
    assert "OpenSpec change of terminal card is still active" in result.stdout
    assert "walk-forward-gate" in result.stdout
    assert "package=no" in result.stdout


def test_audit_does_not_flag_change_of_non_terminal_card(tmp_path: Path, monkeypatch):
    changes = [("card-300-ativa", True, "")]
    board_cards = [(300, "Em desenvolvimento", "Change ativa em andamento")]
    result = _audit_with_terminal_changes(
        tmp_path, monkeypatch, changes=changes, board_cards=board_cards, release_cards="300"
    )

    assert result.returncode == 0
    assert "No active OpenSpec changes mapped to terminal cards" in result.stdout
    assert "OpenSpec change of terminal card is still active" not in result.stdout


def test_audit_low_title_score_reports_unmapped_change(tmp_path: Path, monkeypatch):
    changes = [("random-widget", True, "Widget aleatório sem relação com cards do board")]
    board_cards = [
        (470, "Pronto", "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout")
    ]
    result = _audit_with_terminal_changes(
        tmp_path, monkeypatch, changes=changes, board_cards=board_cards, release_cards="470"
    )

    assert result.returncode == 0
    assert "random-widget" in result.stdout
    assert "below score floor" in result.stdout
    assert "No active OpenSpec changes mapped to terminal cards" not in result.stdout


def test_post_ambiguity_blocks_package_proof(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_change(
        repo, "genetic", complete=True, proposal="Otimização genética de parâmetros do combo"
    )
    fake_gh = _fake_gh(tmp_path)
    # Dois cards do pacote com títulos que empatam no score (mesma contagem de
    # hits de slug/proposal) → associação ambígua → blocker no post.
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        _board(
            (470, "Pronto", "Otimização genética de parâmetros do combo"),
            (471, "Pronto", "Otimização genética de parâmetros do combo"),
        ),
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    result = _run_guard(repo, release_cards="470,471", fake_gh=fake_gh)

    assert result.returncode == 1
    assert "OpenSpec change without safe card association" in result.stdout
    assert "genetic" in result.stdout
    assert "package=yes" in result.stdout


def test_audit_stop_flagging_after_archive_removal(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_change(repo, "walk-forward-gate", complete=True)
    fake_gh = _fake_gh(tmp_path)
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        _board(
            (
                470,
                "Pronto",
                "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout",
            )
        ),
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")
    monkeypatch.setenv("FAKE_COMMENTS", "")

    before = _run_guard(repo, "audit", release_cards="470", fake_gh=fake_gh)
    assert "OpenSpec change of terminal card is still active" in before.stdout

    _remove_change(repo, "walk-forward-gate")
    after = _run_guard(repo, "audit", release_cards="470", fake_gh=fake_gh)
    assert after.returncode == 0
    assert "No active OpenSpec changes mapped to terminal cards" in after.stdout
    assert "OpenSpec change of terminal card is still active" not in after.stdout


def test_audit_terminal_check_keeps_single_board_and_pr_snapshot(tmp_path: Path, monkeypatch):
    repo = _init_repo(tmp_path)
    _make_change(repo, "walk-forward-gate", complete=True)
    fake_gh = _fake_gh(tmp_path)
    call_log = tmp_path / "calls.log"
    monkeypatch.setenv("GH_CALL_LOG", str(call_log))
    monkeypatch.setenv(
        "FAKE_BOARD_JSON",
        _board(
            (
                470,
                "Pronto",
                "Gate walk-forward com split treino/holdout e veredito GO/NO-GO no holdout",
            )
        ),
    )
    monkeypatch.setenv("FAKE_PR_JSON", "[]")

    result = _run_guard(repo, "audit", release_cards="470", fake_gh=fake_gh)

    assert result.returncode == 0
    assert _call_count(call_log, "CALL project item-list") == 1
    assert _call_count(call_log, "CALL pr list") == 1
