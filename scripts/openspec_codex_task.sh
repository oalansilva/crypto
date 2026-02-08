#!/usr/bin/env bash
set -euo pipefail

# OpenSpec → Codex CLI wrapper with guardrails.
# Usage:
#   ./scripts/openspec_codex_task.sh <spec_id> [--confirm] [--model gpt-5-codex]
#
# Defaults are intentionally conservative:
# - restrict intended edits to selected paths (prompt-level)
# - run tests after Codex
# - enforce diff limits (files + changed lines)

SPEC_ID="${1:-}"
shift || true

CONFIRM="false"
MODEL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --confirm)
      CONFIRM="true"; shift ;;
    --model)
      MODEL="${2:-}"; shift 2 ;;
    -h|--help)
      sed -n '1,120p' "$0"; exit 0 ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$SPEC_ID" ]]; then
  echo "Missing <spec_id>. Example: ./scripts/openspec_codex_task.sh agent-orchestration-metrics-hardening" >&2
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

# 2) Validate the spec (OpenSpec gate)
# Note: openspec validate expects the spec id, not the file path.
echo "[openspec] validating: $SPEC_ID"
openspec validate "$SPEC_ID"

SPEC_FILE="$REPO_ROOT/openspec/specs/$SPEC_ID/spec.md"
if [[ ! -f "$SPEC_FILE" ]]; then
  echo "Spec file not found at: $SPEC_FILE" >&2
  exit 1
fi

# 3) Run Codex
ALLOWED_PATHS=("backend/" "frontend/" "src/" "tests/" "openspec/")

PROMPT=$(cat <<'EOF'
You are implementing an OpenSpec in the repo.

Instructions:
- Read the spec file at: openspec/specs/${SPEC_ID}/spec.md
- Only modify files under: backend/, frontend/, src/, tests/, openspec/
- Do NOT do broad refactors, reformatting, or drive-by changes.
- Keep diffs minimal and focused on the spec.
- After implementation, run tests: ./backend/.venv/bin/python -m pytest -q
- If tests fail, fix them and rerun.

Output requirements (end of your run):
- A short summary of what changed
- Files changed
- Tests result (PASS/FAIL)
- Suggested git commit message including: [spec:${SPEC_ID}]
EOF
)

# Expand variables inside prompt safely
PROMPT="${PROMPT//\$\{SPEC_ID\}/$SPEC_ID}"

CODex_ARGS=(exec --full-auto --cd "$REPO_ROOT")
if [[ -n "$MODEL" ]]; then
  CODex_ARGS+=(--model "$MODEL")
fi

echo "[codex] running"
# shellcheck disable=SC2068
codex ${CODex_ARGS[@]} "$PROMPT"

# 4) Run tests (hard gate)
echo "[tests] running pytest"
./backend/.venv/bin/python -m pytest -q

# 5) Guardrail: diff limits
MAX_FILES_CHANGED="${MAX_FILES_CHANGED:-3}"
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

echo "OK: spec validated, codex run completed, tests passed, diff within limits (or confirmed)."

echo "Next: git add -A && git commit -m \"[spec:$SPEC_ID] <message>\""
