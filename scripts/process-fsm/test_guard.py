from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from fsm import load_fsm  # noqa: E402
from guard import decide, extract_path  # noqa: E402
from resolve import UNBOUND  # noqa: E402

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

DENY_STATES = (
    "Todo",
    "Design",
    "Aprovação de Design",
    "Pronto para Dev",
    "QA",
    "Done",
    "Homologado",
    "Pronto",
    "Cancelado",
)
ALLOW_STATES = ("Em desenvolvimento", "Code Review")
SILENT = lambda bound: (_ for _ in ()).throw(AssertionError(f"github called bound={bound}"))  # noqa: E731


def _no_github(_bound: str | None) -> str | None:
    return None


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def _init_repo(path: Path, branch: str, filename: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", branch, str(path)], check=True, capture_output=True, text=True)
    _run_git(path, "config", "user.email", "process-fsm@test.local")
    _run_git(path, "config", "user.name", "process-fsm")
    tracked = path / filename
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("fixture\n", encoding="utf-8")
    _run_git(path, "add", filename)
    _run_git(path, "commit", "-m", "init")
    return tracked


def _write_payload(cwd: Path, rel: str, status: str | None = None, tool: str = "Write") -> dict:
    tool_input = {"target_notebook": rel} if tool == "EditNotebook" else {"path": rel}
    payload: dict = {"tool_name": tool, "tool_input": tool_input, "cwd": str(cwd)}
    if status is not None:
        payload["status"] = status
    return payload


def _shell_payload(cwd: Path, command: str, status: str | None = None) -> dict:
    payload: dict = {"command": command, "cwd": str(cwd)}
    if status is not None:
        payload["status"] = status
    return payload


def test_extract_path_from_cursor_envelope():
    assert extract_path({"tool_name": "Write", "tool_input": {"path": "backend/a.py"}}) == "backend/a.py"
    assert extract_path({"tool_name": "StrReplace", "tool_input": {"file_path": "backend/a.py"}}) == "backend/a.py"
    assert extract_path({"tool_name": "EditNotebook", "tool_input": {"target_notebook": "backend/n.ipynb"}}) == (
        "backend/n.ipynb"
    )
    assert extract_path({"command": "cat >backend/app/main.py", "cwd": "/"}) == "backend/app/main.py"
    assert extract_path({"command": "tee /tmp/repo/backend/app/main.py", "cwd": "/"}) == "/tmp/repo/backend/app/main.py"
    assert extract_path({"command": "pytest backend/ -q", "cwd": "/"}) is None


@pytest.mark.parametrize("state", DENY_STATES)
def test_product_write_denied_in_column(tmp_path: Path, state: str):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py", status=state)
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"
    assert "reason=" in result["agent_message"]
    if state == "Pronto para Dev":
        assert "I3" in result["agent_message"]


@pytest.mark.parametrize("state", ALLOW_STATES)
@pytest.mark.parametrize("tool", ["Write", "StrReplace", "Delete", "EditNotebook"])
def test_product_write_allowed_under_i1(tmp_path: Path, state: str, tool: str):
    repo = tmp_path / "card"
    rel = "backend/app/main.py" if tool != "EditNotebook" else "backend/notebook.ipynb"
    _init_repo(repo, "card-611-process-fsm-guard", rel)
    payload = _write_payload(repo, rel, status=state, tool=tool)
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_injected_status_does_not_call_provider(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_develop_write_denied(tmp_path: Path):
    repo = tmp_path / "develop"
    _init_repo(repo, "develop", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"
    assert "develop-write" in result["agent_message"] or "I1" in result["agent_message"]


def test_main_write_denied(tmp_path: Path):
    repo = tmp_path / "main"
    _init_repo(repo, "main", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"


def test_unbound_write_denied(tmp_path: Path):
    repo = tmp_path / "change"
    _init_repo(repo, "change-608-process-fsm", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"
    assert "unbound" in result["agent_message"] or "unbound-write" in result["agent_message"]


def test_bound_mismatch_denied(tmp_path: Path):
    cwd_repo = tmp_path / "card-605"
    path_repo = tmp_path / "card-611"
    _init_repo(cwd_repo, "card-605-other", "tracked.txt")
    tracked = _init_repo(path_repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = {
        "tool_name": "Write",
        "tool_input": {"path": str(tracked)},
        "cwd": str(cwd_repo),
        "status": "Em desenvolvimento",
    }
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"


def test_replay_b6a71170(tmp_path: Path):
    repo = tmp_path / "develop"
    _init_repo(repo, "develop", "backend/app/tasks/discovery_tasks.py")
    payload = _write_payload(repo, "backend/app/tasks/discovery_tasks.py", status="Todo")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"


def test_design_openspec_write_skips_evaluate(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "openspec/changes/card-611-x/proposal.md")
    calls: list = []

    def wrapped(fsm, ctx):
        calls.append(ctx)
        raise AssertionError("evaluate must not run for design_globs")

    payload = _write_payload(repo, "openspec/changes/card-611-x/proposal.md", status="Design")
    result = decide(payload, status_provider=SILENT, evaluate_fn=wrapped)
    assert result["permission"] == "allow"
    assert calls == []


def test_prototype_write_allowed_in_design(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "frontend/public/prototypes/x/index.html")
    payload = _write_payload(repo, "frontend/public/prototypes/x/index.html", status="Design")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_fail_closed_product_denied(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _write_payload(repo, "backend/app/main.py")
    result = decide(payload, status_provider=_no_github)
    assert result["permission"] == "deny"
    assert "fail_closed" in result["agent_message"]


def test_fail_closed_design_allowed_on_card_branch(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "openspec/changes/card-611-x/design.md")
    payload = _write_payload(repo, "openspec/changes/card-611-x/design.md")
    result = decide(payload, status_provider=_no_github)
    assert result["permission"] == "allow"


def test_shell_redirect_denied(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _shell_payload(repo, "cat extra >> backend/app/main.py", status="Todo")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"


def test_shell_tee_denied(tmp_path: Path):
    repo = tmp_path / "develop"
    _init_repo(repo, "develop", "backend/app/main.py")
    payload = _shell_payload(repo, "echo x | tee backend/app/main.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "deny"


def test_write_into_missing_product_dir_still_binds(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _write_payload(repo, "backend/newpkg/mod.py", status="Em desenvolvimento")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_shell_absolute_and_glued_redirect_denied(tmp_path: Path):
    repo = tmp_path / "card"
    tracked = _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    abs_path = str(tracked)
    glued = _shell_payload(repo, "cat >backend/app/main.py", status="Todo")
    absolute = _shell_payload(repo, f"tee {abs_path}", status="Todo")
    assert decide(glued, status_provider=SILENT)["permission"] == "deny"
    assert decide(absolute, status_provider=SILENT)["permission"] == "deny"


def test_pytest_backend_allowed(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _shell_payload(repo, "pytest backend/ -q", status="Todo")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_git_commit_not_gated(tmp_path: Path):
    repo = tmp_path / "card"
    _init_repo(repo, "card-611-process-fsm-guard", "backend/app/main.py")
    payload = _shell_payload(repo, "git commit -m 'feat: backend'", status="Todo")
    result = decide(payload, status_provider=SILENT)
    assert result["permission"] == "allow"


def test_hooks_json_composes_impeccable():
    hooks = json.loads((REPO / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    pre = hooks["hooks"]["preToolUse"]
    assert pre[0]["command"] == ".cursor/hooks/process-fsm-guard.sh"
    assert pre[0]["failClosed"] is True
    assert "Write" in pre[0]["matcher"]
    shell = hooks["hooks"]["beforeShellExecution"]
    assert shell[0]["command"] == ".cursor/hooks/process-fsm-guard.sh"
    assert shell[0].get("failClosed") is not True
    assert hooks["hooks"]["afterFileEdit"][0]["command"].endswith("impeccable.sh afterFileEdit")
    assert hooks["hooks"]["stop"][0]["command"].endswith("impeccable.sh stop")
    assert (REPO / ".cursor" / "hooks" / "impeccable.sh").is_file()


def test_fsm_still_loads():
    validate = load_fsm()
    assert validate["fail_closed_asymmetric"] is True
