from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from fsm import load_fsm  # noqa: E402
from paging import UNBOUND_PAGE, page  # noqa: E402
from resolve import UNBOUND  # noqa: E402

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

TODO_STUB = "Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda."
HOMOLOGADO_STUB = "Lote; não é main. T16 só com M_lote."
PLAYBOOK = ("release-guard", "subir lote", "deploy PROD")


def _silent(_bound: str | None) -> str | None:
    raise AssertionError(f"github called bound={_bound}")


def _resolve(bound: str, git: str) -> object:
    def inner(cwd, path, issue_id=None, status=None):
        return {"q": None, "bound_card": bound, "q_git": git}

    return inner


def _provider(status: str | None):
    def inner(bound: str | None) -> str | None:
        assert bound == "613"
        return status

    return inner


def _line_count(text: str) -> int:
    return len(text.splitlines())


def test_todo_page_omits_release_playbook():
    result = page(
        cwd=".",
        resolve_fn=_resolve("613", "card-613-process-fsm-paging"),
        status_provider=_provider("Todo"),
    )
    ctx = result["additional_context"]
    assert TODO_STUB in ctx
    assert "q=Todo" in ctx
    assert "bound_card=613" in ctx
    for needle in PLAYBOOK:
        assert needle not in ctx
    assert _line_count(ctx) <= 20


def test_homologado_page_is_not_release_playbook():
    result = page(
        cwd=".",
        resolve_fn=_resolve("613", "card-613-process-fsm-paging"),
        status_provider=_provider("Homologado"),
    )
    ctx = result["additional_context"]
    assert HOMOLOGADO_STUB in ctx
    assert "release-guard pre" not in ctx
    assert "release-guard post" not in ctx
    assert "deploy PROD" not in ctx
    assert _line_count(ctx) <= 20


def test_unbound_does_not_load_homologado():
    result = page(
        cwd=".",
        resolve_fn=_resolve(UNBOUND, "develop"),
        status_provider=_silent,
    )
    ctx = result["additional_context"]
    assert UNBOUND_PAGE in ctx
    assert HOMOLOGADO_STUB not in ctx
    for needle in PLAYBOOK:
        assert needle not in ctx
    assert "bound_card=⊥" in ctx


def test_missing_status_is_unbound_stub():
    result = page(
        cwd=".",
        resolve_fn=_resolve("613", "card-613-process-fsm-paging"),
        status_provider=_provider(None),
    )
    ctx = result["additional_context"]
    assert UNBOUND_PAGE in ctx
    assert HOMOLOGADO_STUB not in ctx


def test_page_uses_yaml_stubs():
    fsm = load_fsm()
    assert TODO_STUB in str(fsm["context_file"]["Todo"])
    assert HOMOLOGADO_STUB in str(fsm["context_file"]["Homologado"])


def _harness_body_lines() -> list[str]:
    text = (REPO / ".cursor" / "rules" / "harness.mdc").read_text(encoding="utf-8")
    assert text.startswith("---")
    rest = text[3:]
    end = rest.find("\n---")
    body = rest[end + 4 :] if end != -1 else rest
    return [ln for ln in body.splitlines() if ln.strip()]


def test_harness_mdc_body_budget():
    lines = _harness_body_lines()
    text = "\n".join(lines)
    assert 8 <= len(lines) <= 15
    assert "Em Refinamento" in text
    assert "(q, bound_card, q_git)" in text
    assert "diff-reviewer" not in text
    assert "release-guard" not in text


def test_agents_md_is_stub():
    text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    nonempty = [ln for ln in text.splitlines() if ln.strip()]
    assert len(nonempty) <= 40
    assert "docs/crypto-overlay.md" in text
    assert "github.com/users/oalansilva/projects/1" in text
    assert "scripts/release-guard pre" not in text
    assert "Em Refinamento -> Todo -> Design" not in text


def test_skill_priority_anchor():
    text = (REPO / ".cursor" / "skills" / "alan-workflow" / "SKILL.md").read_text(encoding="utf-8")
    assert "δ e Guard > overlay > skill > wording" in text
    assert "1. Instrução direta de Alan no chat." not in text


def test_hooks_json_session_start():
    hooks = json.loads((REPO / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    start = hooks["hooks"]["sessionStart"]
    assert start[0]["command"] == ".cursor/hooks/process-fsm-session-start.sh"
    assert start[0].get("failClosed") is not True
    pre = hooks["hooks"]["preToolUse"]
    assert pre[0]["command"] == ".cursor/hooks/process-fsm-guard.sh"
    assert pre[0]["failClosed"] is True
    assert hooks["hooks"]["beforeShellExecution"][0]["command"] == ".cursor/hooks/process-fsm-guard.sh"
    assert hooks["hooks"]["afterFileEdit"][0]["command"].endswith("impeccable.sh afterFileEdit")
    assert hooks["hooks"]["stop"][0]["command"].endswith("impeccable.sh stop")
    assert (REPO / ".cursor" / "hooks" / "impeccable.sh").is_file()
    adapter = REPO / ".cursor" / "hooks" / "process-fsm-session-start.sh"
    assert adapter.is_file()
    assert adapter.stat().st_mode & stat.S_IXUSR


def test_session_start_adapter_fallback(tmp_path: Path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_py = fake_bin / "python3"
    fake_py.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    fake_py.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
    proc = subprocess.run(
        [str(REPO / ".cursor" / "hooks" / "process-fsm-session-start.sh")],
        input="{}",
        capture_output=True,
        text=True,
        env=env,
        cwd=str(REPO),
        check=False,
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    ctx = data["additional_context"]
    assert UNBOUND_PAGE in ctx
    assert "docs/crypto-overlay.md" not in ctx
    assert "release-guard" not in ctx
