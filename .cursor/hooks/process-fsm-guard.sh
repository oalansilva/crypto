#!/usr/bin/env bash
# Cursor adapter: process-fsm Guard Write. Always emit JSON (failClosed on Write).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GUARD="$ROOT/scripts/process-fsm/guard.py"
RAW="$(cat)"

emit() {
  printf '%s\n' "$1"
}

fallback() {
  # Decision 12: prefix-match without PyYAML (stdlib json + git only).
  PROCESS_FSM_RAW="$RAW" PROCESS_FSM_ROOT="$ROOT" python3 - <<'PY' 2>/dev/null || true
import json, os, re, subprocess, sys

raw = os.environ.get("PROCESS_FSM_RAW") or ""
try:
    payload = json.loads(raw) if raw.strip() else {}
except json.JSONDecodeError:
    payload = {}
if not isinstance(payload, dict):
    payload = {}

cwd = str(payload.get("cwd") or payload.get("workspaceRoot") or os.getcwd())
tool = str(payload.get("tool_name") or payload.get("toolName") or "")
data = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
if not data:
    gi = payload.get("toolInput")
    if isinstance(gi, dict):
        data = gi
    elif isinstance(gi, str) and gi.strip():
        try:
            parsed = json.loads(gi)
        except json.JSONDecodeError:
            parsed = {}
        data = parsed if isinstance(parsed, dict) else {}
path = None
for key in ("path", "file_path", "file", "target_file", "target_notebook"):
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        path = value.strip()
        break
command = payload.get("command") if isinstance(payload.get("command"), str) else ""
if not command:
    nested = data.get("command")
    command = nested if isinstance(nested, str) else ""
if "item-edit" in command and (
    "PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM" in command
    or "updateProjectV2ItemFieldValue" in command
    or any(x in command for x in (
        "fed46e78", "4c26ac72", "bd47fbe8", "b45bf4aa", "0257f58c", "fe1ad960",
        "b1858de0", "9220bf8c", "e02597eb", "dfcb47b5", "8ca47888", "ce5cd459",
    ))
):
    msg = "process-fsm-guard deny reason=status_item_edit. Use process_event."
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
    sys.exit(0)
if "updateProjectV2ItemFieldValue" in command and "PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM" in command:
    msg = "process-fsm-guard deny reason=status_item_edit. Use process_event."
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
    sys.exit(0)
# Card #631: deny sidecar only on mutation, not mere citation.
sys.path.insert(0, os.path.join(os.environ.get("PROCESS_FSM_ROOT", ""), "scripts", "process-fsm"))
try:
    from board_status import is_sidecar_path as _is_sidecar_path
    from board_status import sidecar_mutation_in_command as _sidecar_mut
except Exception:
    def _is_sidecar_path(p):
        return bool(p) and str(p).replace("\\", "/").endswith(".design-digest")
    def _sidecar_mut(c):
        return False
if _sidecar_mut(command) or _is_sidecar_path(path):
    msg = "process-fsm-guard deny reason=sidecar"
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
    sys.exit(0)
if path is None and command:
    import os as _os
    non_redir = re.search(r"(?:sed\s+-i|perl\s+-i|\bcp\s+|\bmv\s+|\binstall\s+)", command)
    targets = []
    for m in re.finditer(r"(?:\d*)?(>>|>)\s*([^\s|;<>&]+)", command):
        t = m.group(2).strip().strip("'\"")
        if t.startswith("&"):
            continue
        targets.append(t)
    for m in re.finditer(r"\btee(?:\s+-a)?\s+([^\s|;<>&]+)", command):
        targets.append(m.group(1).strip().strip("'\""))
    def allowlisted(t):
        if t == "/dev/null":
            return True
        if t == "/tmp" or t.startswith("/tmp/"):
            real_t = _os.path.realpath(t)
            real_c = _os.path.realpath(cwd)
            if real_t == real_c or real_t.startswith(real_c + _os.sep):
                return False
            return True
        return False
    if (targets and all(allowlisted(t) for t in targets) and not non_redir) or (not targets and not non_redir):
        path = None
    else:
        product_hit = None
        for t in targets:
            if allowlisted(t):
                continue
            if (
                t.startswith("backend/")
                or t.startswith("frontend/src/")
                or t.startswith("openspec/changes/")
                or t.startswith("frontend/public/prototypes/")
                or "/backend/" in t
                or "/frontend/src/" in t
                or "/openspec/changes/" in t
                or "/frontend/public/prototypes/" in t
            ):
                product_hit = t
                break
        if product_hit:
            path = product_hit
        elif non_redir or any(not allowlisted(t) for t in targets):
            match = re.search(
                r"((?:/(?:[\w.-]+))*/(?:backend|frontend/src|openspec/changes|frontend/public/prototypes)/[^\s'\"|;<>&]+|"
                r"(?:backend|frontend/src|openspec/changes|frontend/public/prototypes)/[^\s'\"|;<>&]+)",
                command,
            )
            if match:
                path = match.group(1)
                if path.startswith("./"):
                    path = path[2:]
if not path:
    print(json.dumps({"permission": "allow", "decision": "allow", "reason": ""}))
    sys.exit(0)

posix = path.replace("\\", "/")
if posix.startswith("./"):
    posix = posix[2:]
if posix.endswith(".design-digest"):
    msg = "process-fsm-guard deny reason=sidecar"
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
    sys.exit(0)
for marker in ("/backend/", "/frontend/src/", "/openspec/changes/", "/frontend/public/prototypes/"):
    idx = posix.find(marker)
    if idx != -1:
        posix = posix[idx + 1 :]
        break
is_product = posix.startswith("backend/") or posix.startswith("frontend/src/")
is_design = posix.startswith("openspec/changes/") or posix.startswith("frontend/public/prototypes/")
target = path if os.path.isabs(path) else os.path.join(cwd, path)
git_dir = target if os.path.isdir(target) else os.path.dirname(target) or cwd
while git_dir and not os.path.isdir(git_dir):
    parent = os.path.dirname(git_dir)
    if parent == git_dir:
        git_dir = cwd
        break
    git_dir = parent
env = os.environ.copy()
for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
    env.pop(key, None)
try:
    proc = subprocess.run(
        ["git", "-C", git_dir, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, timeout=5, env=env, check=False,
    )
    branch = (proc.stdout or "").strip()
except (OSError, subprocess.TimeoutExpired):
    branch = ""
card = bool(re.match(r"^card-\d+(?:-.*)?$", branch or ""))
msg = "process-fsm-guard deny reason=fail_closed (python fallback)"
if is_product:
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
elif is_design and card:
    print(json.dumps({"permission": "allow", "decision": "allow", "reason": ""}))
elif is_design:
    print(json.dumps({"permission": "deny", "decision": "deny", "agent_message": msg, "user_message": msg, "reason": msg}))
else:
    print(json.dumps({"permission": "allow", "decision": "allow", "reason": ""}))
PY
}

PY=""
if [[ -x "$ROOT/backend/.venv/bin/python" ]]; then
  PY="$ROOT/backend/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
fi

if [[ -n "$PY" && -f "$GUARD" ]]; then
  OUT="$(printf '%s' "$RAW" | "$PY" "$GUARD" 2>/dev/null || true)"
  if printf '%s' "$OUT" | grep -q '"permission"'; then
    emit "$OUT"
    exit 0
  fi
fi

FB="$(fallback || true)"
if printf '%s' "$FB" | grep -q '"permission"'; then
  emit "$FB"
  exit 0
fi

emit '{"permission":"deny","decision":"deny","agent_message":"process-fsm-guard deny reason=fail_closed","user_message":"process-fsm-guard deny reason=fail_closed","reason":"process-fsm-guard deny reason=fail_closed"}'
exit 0
