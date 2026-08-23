"""Compile process-fsm.yaml + resolver into a Write Guard (Cursor + Grok).

Glob-first: evaluate(write_produto) only for product_globs. No GitHub in unit tests.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board_status import (  # noqa: E402
    is_sidecar_path,
    is_status_edit_command,
    sidecar_in_command,
)
from fsm import CARD_GIT_RE, EvalContext, EvalResult, evaluate, load_fsm  # noqa: E402
from resolve import UNBOUND, resolve  # noqa: E402

REPO_ROOT = ROOT.parents[1]
WRITE_TOOLS = frozenset(
    {
        "Write",
        "StrReplace",
        "Delete",
        "EditNotebook",
        "write",
        "search_replace",
        "Edit",
        "MultiEdit",
    }
)
SHELL_TOOLS = frozenset({"Shell", "Bash", "run_terminal_command", "run_terminal_cmd"})
PATH_KEYS = ("path", "file_path", "file", "target_file", "target_notebook")
MUTATION_RE = re.compile(r"(?:>>|>|\btee\s+|sed\s+-i|perl\s+-i|\bcp\s+|\bmv\s+|\binstall\s+)")
NON_REDIRECT_MUTATION_RE = re.compile(r"(?:sed\s+-i|perl\s+-i|\bcp\s+|\bmv\s+|\binstall\s+)")
# File redirects / tee destinations. Targets starting with & are fd redirects (2>&1).
FILE_REDIRECT_RE = re.compile(r"(?:\d*)?(>>|>)\s*([^\s|;<>&]+)")
TEE_TARGET_RE = re.compile(r"\btee(?:\s+-a)?\s+([^\s|;<>&]+)")
PRODUCT_IN_CMD_RE = re.compile(
    r"((?:/(?:[\w.-]+))*/(?:backend|frontend/src)/[^\s'\"|;<>&]+|"
    r"(?:backend|frontend/src)/[^\s'\"|;<>&]+)"
)
DESIGN_IN_CMD_RE = re.compile(
    r"((?:/(?:[\w.-]+))*/(?:openspec/changes|frontend/public/prototypes)/[^\s'\"|;<>&]+|"
    r"(?:openspec/changes|frontend/public/prototypes)/[^\s'\"|;<>&]+)"
)

StatusProvider = Callable[[str | None], str | None]
EvaluateFn = Callable[[dict[str, Any], EvalContext], EvalResult]
ResolveFn = Callable[..., dict[str, str | None]]


def _prefixes(globs: list[Any]) -> tuple[str, ...]:
    out: list[str] = []
    for item in globs:
        text = str(item).replace("\\", "/").rstrip("*")
        text = text.rstrip("/")
        if text:
            out.append(text + "/")
    return tuple(out)


def glob_kind(rel: str, fsm: Mapping[str, Any]) -> str:
    posix = rel.replace("\\", "/")
    if posix.startswith("./"):
        posix = posix[2:]
    for prefix in _prefixes(list(fsm.get("product_globs") or [])):
        if posix == prefix[:-1] or posix.startswith(prefix):
            return "product"
    for prefix in _prefixes(list(fsm.get("design_globs") or [])):
        if posix == prefix[:-1] or posix.startswith(prefix):
            return "design"
    return "other"


def repo_relative(cwd: Path, path: str) -> str:
    candidate = Path(path)
    resolved = candidate if candidate.is_absolute() else (cwd / candidate)
    try:
        return resolved.resolve().relative_to(cwd.resolve()).as_posix()
    except ValueError:
        text = resolved.as_posix()
        for marker in (
            "/backend/",
            "/frontend/src/",
            "/openspec/changes/",
            "/frontend/public/prototypes/",
        ):
            idx = text.find(marker)
            if idx != -1:
                return text[idx + 1 :]
        return Path(path).as_posix().removeprefix("./")


def _first_str(mapping: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _as_dict(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _tool_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = _as_dict(payload.get("tool_input"))
    if data:
        return data
    return _as_dict(payload.get("toolInput"))


def normalize(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Canonical envelope: Cursor snake_case and Grok camelCase both work."""
    src = payload if isinstance(payload, Mapping) else {}
    tool = _first_str(src, "tool_name", "toolName") or ""
    cwd = _first_str(src, "cwd") or _first_str(src, "workspaceRoot") or os.getcwd()
    data = _tool_input(src)
    command = src.get("command") if isinstance(src.get("command"), str) else ""
    if not str(command).strip():
        nested = data.get("command")
        command = nested.strip() if isinstance(nested, str) and nested.strip() else ""
    out: dict[str, Any] = {
        "tool_name": tool,
        "tool_input": data,
        "command": command,
        "cwd": cwd,
    }
    status = src.get("status")
    if isinstance(status, str) and status.strip():
        out["status"] = status.strip()
    return out


def emit(permission: str, message: str = "") -> dict[str, str]:
    """Dual Cursor (`permission`) + Grok (`decision`) JSON."""
    allowed = permission == "allow"
    token = "allow" if allowed else "deny"
    out = {
        "permission": token,
        "decision": token,
        "reason": "" if allowed else message,
        "agent_message": "" if allowed else message,
        "user_message": "" if allowed else message,
    }
    return out


def _path_from_write(payload: Mapping[str, Any]) -> str | None:
    data = _tool_input(payload)
    keys = PATH_KEYS
    tool = str(payload.get("tool_name") or "")
    if tool == "EditNotebook":
        keys = ("target_notebook",) + PATH_KEYS
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _strip_quotes(token: str) -> str:
    text = token.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1]
    return text


def _is_allowlisted_sink(target: str, cwd: Path | None = None) -> bool:
    """Card #625: /dev/null and /tmp sinks outside the worktree are not product writes.

    Paths under the envelope cwd still count as product even when pytest uses /tmp
    for the fixture repo (absolute tee into the worktree must remain deny).
    """
    text = _strip_quotes(target)
    if text == "/dev/null":
        return True
    if text == "/tmp" or text.startswith("/tmp/"):
        if cwd is None:
            return True
        try:
            Path(text).resolve().relative_to(cwd.resolve())
        except ValueError:
            return True
        return False
    return False


def _redirect_file_targets(command: str) -> list[str]:
    targets: list[str] = []
    for match in FILE_REDIRECT_RE.finditer(command):
        found = _strip_quotes(match.group(2))
        if found.startswith("&"):
            # fd redirect such as 2>&1 — not a filesystem sink
            continue
        targets.append(found)
    for match in TEE_TARGET_RE.finditer(command):
        targets.append(_strip_quotes(match.group(1)))
    return targets


def _path_from_command(command: str, cwd: Path | None = None) -> str | None:
    if not MUTATION_RE.search(command):
        return None

    targets = _redirect_file_targets(command)
    has_non_redirect = bool(NON_REDIRECT_MUTATION_RE.search(command))

    # Only fd redirects (e.g. 2>&1) and/or allowlisted sinks → do not promote a
    # product path cited elsewhere in the command (card #625 false positive).
    if targets and all(_is_allowlisted_sink(t, cwd) for t in targets) and not has_non_redirect:
        return None
    if not targets and not has_non_redirect:
        return None

    for target in targets:
        if _is_allowlisted_sink(target, cwd):
            continue
        if target.startswith("backend/") or target.startswith("frontend/src/"):
            return target
        if target.startswith("openspec/changes/") or target.startswith(
            "frontend/public/prototypes/"
        ):
            return target
        product = PRODUCT_IN_CMD_RE.search(target)
        design = DESIGN_IN_CMD_RE.search(target)
        if product:
            return product.group(1)
        if design:
            return design.group(1)
        if "/backend/" in target or "/frontend/src/" in target:
            return target
        if "/openspec/changes/" in target or "/frontend/public/prototypes/" in target:
            return target

    match = PRODUCT_IN_CMD_RE.search(command) or DESIGN_IN_CMD_RE.search(command)
    if match is None:
        return None
    found = match.group(1)
    if found.startswith("./"):
        found = found[2:]
    return found


def _command(payload: Mapping[str, Any]) -> str:
    canonical = normalize(payload)
    raw = canonical.get("command")
    return raw.strip() if isinstance(raw, str) and raw.strip() else ""


def _sidecar_deny() -> dict[str, str]:
    message = (
        "process-fsm-guard deny reason=sidecar. .design-digest is written only by process_event T5."
    )
    return emit("deny", message)


def _status_edit_deny() -> dict[str, str]:
    message = (
        "process-fsm-guard deny reason=status_item_edit. Use scripts/process-fsm/process_event.py; "
        "do not gh project item-edit Status."
    )
    return emit("deny", message)


def git_anchor(cwd: Path, path: str) -> str:
    """Existing directory for git -C so Write into a new folder still binds q_git."""
    candidate = Path(path)
    resolved = candidate if candidate.is_absolute() else (cwd / candidate)
    current = resolved.parent
    while not current.exists() and current != current.parent:
        current = current.parent
    return str(current if current.exists() else cwd)


def extract_path(payload: Mapping[str, Any]) -> str | None:
    canonical = normalize(payload)
    tool = str(canonical.get("tool_name") or "")
    cwd_raw = canonical.get("cwd")
    cwd = Path(str(cwd_raw)) if isinstance(cwd_raw, str) and cwd_raw.strip() else None
    if tool in WRITE_TOOLS:
        return _path_from_write(canonical)
    command = canonical.get("command")
    if isinstance(command, str) and command.strip():
        return _path_from_command(command, cwd)
    if tool in SHELL_TOOLS:
        return _path_from_command(str(command or ""), cwd)
    return None


def github_status_provider(bound_card: str | None) -> str | None:
    """Pontual issue→Status. Never used by pytest (tests inject status_provider)."""
    if bound_card in (None, "", UNBOUND):
        return None
    try:
        number = int(str(bound_card))
    except (TypeError, ValueError):
        return None
    env = os.environ.copy()
    try:
        query = (
            'query($n:Int!){repository(owner:"oalansilva",name:"crypto")'
            "{issue(number:$n){projectItems(first:20){nodes{"
            "project{number owner{...on User{login}}}"
            'fieldValueByName(name:"Status")'
            "{...on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}"
        )
        proc = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={query}",
                "-F",
                f"n={number}",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    nodes = (
        (((data.get("data") or {}).get("repository") or {}).get("issue") or {}).get("projectItems")
        or {}
    ).get("nodes") or []
    for node in nodes:
        project = (node or {}).get("project") or {}
        owner = (project.get("owner") or {}).get("login")
        if project.get("number") != 1 or owner not in (None, "oalansilva"):
            continue
        field = (node or {}).get("fieldValueByName") or {}
        name = field.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return None


def _card_branch(q_git: str | None) -> bool:
    return bool(q_git) and CARD_GIT_RE.match(str(q_git)) is not None


def _reason_message(reason: str, state: str | None, q_git: str | None, bound: str | None) -> str:
    return (
        f"process-fsm-guard deny reason={reason} q={state!s} q_git={q_git!s} "
        f"bound_card={bound!s}. Write produto blocked."
    )


def _allow() -> dict[str, str]:
    return emit("allow")


def _deny(reason: str, state: str | None, q_git: str | None, bound: str | None) -> dict[str, str]:
    return emit("deny", _reason_message(reason, state, q_git, bound))


def decide(
    payload: Mapping[str, Any],
    *,
    fsm: dict[str, Any] | None = None,
    resolve_fn: ResolveFn = resolve,
    status_provider: StatusProvider | None = None,
    evaluate_fn: EvaluateFn = evaluate,
    load_fsm_fn: Callable[..., dict[str, Any]] = load_fsm,
) -> dict[str, str]:
    canonical = normalize(payload)
    cwd_raw = canonical.get("cwd") or os.getcwd()
    cwd = Path(str(cwd_raw))
    path = extract_path(canonical)
    command = _command(canonical)
    if is_sidecar_path(path) or sidecar_in_command(command):
        return _sidecar_deny()
    if is_status_edit_command(command):
        return _status_edit_deny()
    if not path:
        return _allow()

    table = fsm if fsm is not None else load_fsm_fn()
    rel = repo_relative(cwd, path)
    kind = glob_kind(rel, table)
    injected = payload.get("status")
    status = injected if isinstance(injected, str) and injected.strip() else None

    resolved = resolve_fn(cwd, git_anchor(cwd, path), status=status)
    q_git = resolved.get("q_git")
    bound = resolved.get("bound_card")
    q: str | None = status if status is not None else resolved.get("q")
    if q is None and status_provider is not None:
        q = status_provider(None if bound in (None, UNBOUND) else str(bound))

    if kind != "product":
        if q is None and kind == "design" and not _card_branch(q_git):
            return _deny("fail_closed", q, q_git, bound)
        return _allow()

    if q is None:
        return _deny("fail_closed", q, q_git, bound)

    ctx = EvalContext(
        state=q,
        event="write_produto",
        actor="Agent",
        q_git=q_git,
        bound_card=bound,
        path=rel,
    )
    result = evaluate_fn(table, ctx)
    if result.result == "allow":
        return _allow()
    reason = result.reason or "I1"
    if q == "Pronto para Dev" and reason == "I1":
        reason = "I3"
    if bound in (None, "", UNBOUND) and reason == "I1":
        reason = "unbound"
    return _deny(reason, q, q_git, bound)


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    decision = decide(payload, status_provider=github_status_provider)
    json.dump(decision, sys.stdout, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
