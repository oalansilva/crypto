from __future__ import annotations

import os
import subprocess
from pathlib import Path

HELPER = Path(__file__).resolve().parents[3] / "scripts" / "post-card-evidence-comment.sh"


def _fake_gh(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "gh"
    script.write_text(
        """#!/usr/bin/env bash
set -u
if [[ "${1:-} ${2:-}" == "issue view" ]]; then
  printf '%s\\n' "${FAKE_COMMENTS_JSON:?}"
  [[ "${FAKE_FAIL_VIEW:-}" == "1" ]] && exit 1
  exit 0
fi
if [[ "${1:-} ${2:-}" == "issue comment" ]]; then
  touch "${FAKE_POST_MARKER:?}"
  exit 0
fi
printf 'unexpected gh call: %s\\n' "$*" >&2
exit 1
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def _run(
    tmp_path: Path,
    comments_json: str,
    *extra: str,
    fail_view: bool = False,
) -> subprocess.CompletedProcess[str]:
    fake_gh = _fake_gh(tmp_path)
    env = dict(os.environ)
    env["PATH"] = f"{fake_gh.parent}:{env['PATH']}"
    env["FAKE_COMMENTS_JSON"] = comments_json
    env["FAKE_POST_MARKER"] = str(tmp_path / "posted")
    if fail_view:
        env["FAKE_FAIL_VIEW"] = "1"
    return subprocess.run(
        [
            str(HELPER),
            "--transition",
            "homologado",
            "--card",
            "480",
            "--commit",
            "412ed9ad",
            *extra,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_homologado_dry_run_previews_without_posting(tmp_path: Path):
    result = _run(tmp_path, '{"comments":[]}', "--dry-run")

    assert result.returncode == 0
    assert "Homologado por Alan na develop." in result.stdout
    assert "DRY-RUN: no comment posted." in result.stdout
    assert not (tmp_path / "posted").exists()


def test_homologado_deduplicates_ref_less_comment(tmp_path: Path):
    comments = (
        '{"comments":[{"body":"Homologado por Alan na develop.\\n'
        'Apto para próximo pacote de release.","url":"https://example.test/comment"}]}'
    )

    result = _run(tmp_path, comments, "--dry-run")

    assert result.returncode == 0
    assert "DEDUPE:" in result.stdout
    assert not (tmp_path / "posted").exists()


def test_homologado_fails_closed_when_gh_view_fails(tmp_path: Path):
    result = _run(tmp_path, '{"comments":[]}', fail_view=True)

    assert result.returncode == 1
    assert "refusing to post (fail-closed)" in result.stderr
    assert not (tmp_path / "posted").exists()


def test_homologado_fails_closed_for_valid_json_without_comments(tmp_path: Path):
    result = _run(tmp_path, "{}")

    assert result.returncode == 1
    assert "returned invalid JSON" in result.stderr
    assert not (tmp_path / "posted").exists()


def test_homologado_fails_closed_for_invalid_json(tmp_path: Path):
    result = _run(tmp_path, "not-json")

    assert result.returncode == 1
    assert "returned invalid JSON" in result.stderr
    assert not (tmp_path / "posted").exists()


def test_homologado_fails_closed_for_malformed_comment_item(tmp_path: Path):
    result = _run(tmp_path, '{"comments":[null]}')

    assert result.returncode == 1
    assert "returned invalid JSON" in result.stderr
    assert not (tmp_path / "posted").exists()
