#!/usr/bin/env bash
set -euo pipefail

# OpenSpec → Codex CLI wrapper with guardrails.
# Usage:
#   ./scripts/openspec_codex_task.sh <change_id> [--confirm] [--model gpt-5-codex] [--include-repo-docs] [--specs-mode <full|requirements|requirements-no-scenarios>] [--ephemeral] [--codex-json|--json]
#
# Defaults are intentionally conservative:
# - FILE_CHAR_LIMIT=6000 (override via env var)
# - --include-repo-docs=false (AGENTS.md/README.md are not attached unless requested)
# - --specs-mode=requirements
# - --ephemeral=false
# - --codex-json/--json=false
# - restrict intended edits to selected paths (prompt-level)
# - run tests after Codex
# - enforce diff limits (files + changed lines)

CHANGE_ID="${1:-}"
shift || true

CONFIRM="false"
MODEL=""
INCLUDE_REPO_DOCS="false"
SPECS_MODE="requirements"
EPHEMERAL="false"
CODEX_JSON="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm)
      CONFIRM="true"; shift ;;
    --model)
      MODEL="${2:-}"; shift 2 ;;
    --include-repo-docs)
      INCLUDE_REPO_DOCS="true"; shift ;;
    --specs-mode)
      case "${2:-}" in
        full|requirements|requirements-no-scenarios)
          SPECS_MODE="${2:-}"; shift 2 ;;
        *)
          echo "Invalid value for --specs-mode: ${2:-}" >&2
          echo "Allowed: full | requirements | requirements-no-scenarios" >&2
          exit 2
          ;;
      esac
      ;;
    --ephemeral)
      EPHEMERAL="true"; shift ;;
    --codex-json|--json)
      CODEX_JSON="true"; shift ;;
    -h|--help)
      sed -n '1,120p' "$0"; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$CHANGE_ID" ]]; then
  echo "Missing <change_id>. Example: ./scripts/openspec_codex_task.sh os-codex-wrapper-change-driven" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v openspec >/dev/null 2>&1; then
  echo "openspec CLI not found in PATH" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found in PATH. Install: npm i -g @openai/codex" >&2
  exit 1
fi

# 0) Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repo: $REPO_ROOT" >&2
  exit 1
fi

# 1) Pre-flight: clean working tree (optional but safer)
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit/stash first for a clean Codex run." >&2
  echo "If you really want to continue, run after cleaning (recommended)." >&2
  exit 2
fi

# 2) Status check (OpenSpec gate)
echo "[openspec] status check (json)"
openspec status --json >/dev/null

# 3) Validate the change (OpenSpec gate)
echo "[openspec] validating change: $CHANGE_ID"
openspec validate "$CHANGE_ID" --type change

CHANGE_DIR="$REPO_ROOT/openspec/changes/$CHANGE_ID"
if [[ ! -d "$CHANGE_DIR" ]]; then
  echo "Change dir not found at: $CHANGE_DIR" >&2
  echo "Create it with: openspec new change $CHANGE_ID --schema spec-driven --description \"...\"" >&2
  exit 1
fi

TASKS_FILE="$CHANGE_DIR/tasks.md"
if [[ ! -f "$TASKS_FILE" ]]; then
  echo "tasks.md not found at: $TASKS_FILE" >&2
  echo "Generate instructions: openspec instructions tasks --change $CHANGE_ID" >&2
  exit 1
fi

# 2.1) Pull apply instructions (JSON) and ensure tasks are present
APPLY_RAW="$({ openspec instructions apply --change "$CHANGE_ID" --json; } 2>&1)"
APPLY_JSON=$(python3 -c 'import json,sys
s=sys.stdin.read()
idx=s.find("{")
if idx<0:
  raise SystemExit(2)
blob=s[idx:]
try:
  obj=json.loads(blob)
except Exception:
  end=blob.rfind("}")
  if end<0:
    raise
  obj=json.loads(blob[:end+1])
print(json.dumps(obj, ensure_ascii=False))
' <<<"$APPLY_RAW")

TASK_COUNT=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print(len(obj.get("tasks") or []))
' <<<"$APPLY_JSON")

if [[ "$TASK_COUNT" -le 0 ]]; then
  echo "No tasks found for change '$CHANGE_ID' (blocked). Add tasks to $TASKS_FILE and try again." >&2
  exit 2
fi

APPLY_INSTRUCTION=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print(obj.get("instruction") or "")
' <<<"$APPLY_JSON")

# Extract context file paths (proposal/design/tasks + specs glob)
CONTEXT_PROPOSAL=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print((obj.get("contextFiles") or {}).get("proposal") or "")
' <<<"$APPLY_JSON")

CONTEXT_DESIGN=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print((obj.get("contextFiles") or {}).get("design") or "")
' <<<"$APPLY_JSON")

CONTEXT_TASKS=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print((obj.get("contextFiles") or {}).get("tasks") or "")
' <<<"$APPLY_JSON")

CONTEXT_SPECS_GLOB=$(python3 -c 'import json,sys
obj=json.loads(sys.stdin.read() or "{}")
print((obj.get("contextFiles") or {}).get("specs") or "")
' <<<"$APPLY_JSON")

# 3) Run Codex
ALLOWED_PATHS=("backend/" "frontend/" "src/" "tests/" "openspec/")

FILE_CHAR_LIMIT="${FILE_CHAR_LIMIT:-6000}"

_file_len() {
  local path="$1"
  python3 -c 'import sys
p=sys.argv[1]
try:
  with open(p, "r", encoding="utf-8") as f:
    print(len(f.read()))
except Exception:
  print(-1)
' "$path"
}

_read_capped() {
  local path="$1"
  local limit="$2"
  python3 -c 'import sys
p=sys.argv[1]
limit=int(sys.argv[2])
try:
  with open(p, "r", encoding="utf-8") as f:
    data=f.read()
except Exception as e:
  print(f"[ERROR reading file: {e}]")
  raise SystemExit(0)

if limit > 0 and len(data) > limit:
  print(data[:limit])
  print(f"\n[TRUNCATED to {limit} chars]\n")
else:
  print(data)
' "$path" "$limit"
}

_spec_files_from_glob() {
  local glob_expr="$1"
  python3 -c 'import glob, sys
expr=sys.argv[1]
for p in sorted(glob.glob(expr, recursive=True)):
  print(p)
' "$glob_expr"
}

_spec_name_from_path() {
  local path="$1"
  python3 -c 'import re, sys
p=sys.argv[1].replace("\\\\", "/")
m=re.search(r"(?:^|.*/)openspec/changes/[^/]+/specs/([^/]+)/spec\\.md$", p)
print(m.group(1) if m else "")
' "$path"
}

_attach_spec_requirements_json() {
  local spec_name="$1"
  local spec_path="$2"
  local json_payload=""
  local n=0

  if [[ "$SPECS_MODE" == "requirements-no-scenarios" ]]; then
    json_payload="$(openspec show "$spec_name" --type spec --requirements --no-scenarios --json)"
  else
    json_payload="$(openspec show "$spec_name" --type spec --requirements --json)"
  fi

  n="${#json_payload}"
  if [[ "$FILE_CHAR_LIMIT" -gt 0 && "$n" -gt "$FILE_CHAR_LIMIT" ]]; then
    TRUNCATED_REPORT+=("spec:$spec_name requirements-json ($n chars)")
  fi

  PROMPT+=$'\n[CHANGE SPEC REQUIREMENTS JSON] '
  PROMPT+="$spec_name"
  PROMPT+=" ($spec_path)"
  PROMPT+=$'\n'
  if [[ "$FILE_CHAR_LIMIT" -gt 0 && "$n" -gt "$FILE_CHAR_LIMIT" ]]; then
    PROMPT+="${json_payload:0:FILE_CHAR_LIMIT}"
    PROMPT+=$'\n'
    PROMPT+="[TRUNCATED to ${FILE_CHAR_LIMIT} chars]"
    PROMPT+=$'\n'
  else
    PROMPT+="$json_payload"
  fi
}

PROMPT=$(cat <<'EOF'
You are implementing an OpenSpec **change** in this repo.

Change id: ${CHANGE_ID}
Change dir: openspec/changes/${CHANGE_ID}

Rules:
- Use the change artifacts below. `tasks.md` is the execution plan; specs/design are the contract/constraints.
- Implement ONLY what is required by tasks/specs. No broad refactors or reformatting.
- Only modify files under: backend/, frontend/, src/, tests/, openspec/
- After implementation, run tests: ./backend/.venv/bin/python -m pytest -q
- If tests fail, fix them and rerun.
- Use skills do projeto quando aplicável (ex.: ticket-breakdown para dividir tarefas; system-design-draft para arquitetura; unit-test-starter/integration-test-planner para testes; debugging-checklist/error-message-explainer para erros; css-layout-helper/accessibility-basic-check para frontend).

Enriched apply instruction (from OpenSpec):
${APPLY_INSTRUCTION}

---
CHANGE ARTIFACTS (verbatim, may be truncated per-file):
EOF
)

# Attach proposal/design/specs/tasks (+ optional repo AGENTS.md / README.md)
TRUNCATED_REPORT=()

_attach_file() {
  local p="$1"
  [[ -z "$p" ]] && return 0
  [[ ! -f "$p" ]] && return 0

  local n
  n="$(_file_len "$p")"
  if [[ "$FILE_CHAR_LIMIT" -gt 0 && "$n" -gt "$FILE_CHAR_LIMIT" ]]; then
    TRUNCATED_REPORT+=("$p ($n chars)")
  fi

  PROMPT+=$'\n[CHANGE FILE] '
  PROMPT+="$p"
  PROMPT+=$'\n'
  PROMPT+="$(_read_capped "$p" "$FILE_CHAR_LIMIT")"
}

if [[ "$INCLUDE_REPO_DOCS" == "true" ]]; then
  # Repo-level instructions for agents (kept small). These are additive context.
  _attach_file "$REPO_ROOT/AGENTS.md"
  _attach_file "$REPO_ROOT/README.md"
fi

_attach_file "$CONTEXT_PROPOSAL"
_attach_file "$CONTEXT_DESIGN"

if [[ -n "$CONTEXT_SPECS_GLOB" ]]; then
  while IFS= read -r spec_path; do
    [[ -z "$spec_path" ]] && continue
    if [[ "$SPECS_MODE" == "full" ]]; then
      _attach_file "$spec_path"
      continue
    fi

    spec_name="$(_spec_name_from_path "$spec_path")"
    if [[ -z "$spec_name" ]]; then
      echo "[warn] Could not derive spec name from path, attaching full file instead: $spec_path" >&2
      _attach_file "$spec_path"
      continue
    fi
    _attach_spec_requirements_json "$spec_name" "$spec_path"
  done < <(_spec_files_from_glob "$CONTEXT_SPECS_GLOB")
fi

_attach_file "$CONTEXT_TASKS"

if [[ ${#TRUNCATED_REPORT[@]} -gt 0 ]]; then
  echo "[warn] Some change context files exceeded FILE_CHAR_LIMIT=$FILE_CHAR_LIMIT and were truncated in the Codex prompt:" >&2
  for item in "${TRUNCATED_REPORT[@]}"; do
    echo "  - $item" >&2
  done
  echo "[warn] You can increase limit with: FILE_CHAR_LIMIT=<n> ./scripts/openspec_codex_task.sh $CHANGE_ID" >&2
fi

PROMPT+=$(cat <<'EOF'

---
Output requirements (end of your run):
- A short summary of what changed
- Files changed
- Tests result (PASS/FAIL)
- Suggested git commit message including: [change:${CHANGE_ID}]
EOF
)

# Expand variables inside prompt safely
PROMPT="${PROMPT//\$\{CHANGE_ID\}/$CHANGE_ID}"

CODex_ARGS=(exec --full-auto --cd "$REPO_ROOT")
if [[ -n "$MODEL" ]]; then
  CODex_ARGS+=(--model "$MODEL")
fi
if [[ "$EPHEMERAL" == "true" ]]; then
  CODex_ARGS+=(--ephemeral)
fi
if [[ "$CODEX_JSON" == "true" ]]; then
  CODex_ARGS+=(--json)
fi

echo "[codex] running"
# shellcheck disable=SC2068
codex ${CODex_ARGS[@]} "$PROMPT"

# 4) Run tests (hard gate)
echo "[tests] running pytest"
./backend/.venv/bin/python -m pytest -q

# 5) Guardrail: diff limits
MAX_FILES_CHANGED="${MAX_FILES_CHANGED:-10}"
# Default changed: disable strict line-limit by default (was 200).
# Set MAX_LINES_CHANGED to a positive integer to re-enable.
MAX_LINES_CHANGED="${MAX_LINES_CHANGED:-0}"

FILES_CHANGED=$(git diff --name-only | wc -l | tr -d ' ')
LINES_CHANGED=$(git diff --numstat | awk '{add+=$1; del+=$2} END {print add+del+0}')

echo "[diff] files_changed=$FILES_CHANGED (limit=$MAX_FILES_CHANGED)"
echo "[diff] lines_changed=$LINES_CHANGED (limit=$MAX_LINES_CHANGED)"

echo "[diff] summary:"
git diff --stat

over_limit="false"
if [[ "$FILES_CHANGED" -gt "$MAX_FILES_CHANGED" ]]; then over_limit="true"; fi
# If MAX_LINES_CHANGED <= 0, line-limit is disabled.
if [[ "$MAX_LINES_CHANGED" -gt 0 && "$LINES_CHANGED" -gt "$MAX_LINES_CHANGED" ]]; then over_limit="true"; fi

if [[ "$over_limit" == "true" && "$CONFIRM" != "true" ]]; then
  echo "Diff exceeded limits. Review manually and re-run with --confirm if acceptable." >&2
  exit 3
fi

echo "OK: change validated, codex run completed, tests passed, diff within limits (or confirmed)."

echo "Next: git add -A && git commit -m \"[change:$CHANGE_ID] <message>\""
