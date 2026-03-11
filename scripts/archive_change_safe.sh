#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <change-id>" >&2
  exit 1
fi

CHANGE_ID="$1"
PROJECT_SLUG="${PROJECT_SLUG:-crypto}"
WORKFLOW_BASE_URL="${WORKFLOW_BASE_URL:-http://127.0.0.1:8003}"
WORKFLOW_HEALTH_URL="${WORKFLOW_HEALTH_URL:-$WORKFLOW_BASE_URL/api/workflow/health}"
KANBAN_URL="${KANBAN_URL:-$WORKFLOW_BASE_URL/api/workflow/kanban/changes?project_slug=${PROJECT_SLUG}}"

cd "$(dirname "$0")/.."

COORD="docs/coordination/${CHANGE_ID}.md"
TASKS="openspec/changes/${CHANGE_ID}/tasks.md"

PY_BIN="./.venv/bin/python"
if [[ ! -x "$PY_BIN" ]]; then
  PY_BIN="python3"
fi

if [[ ! -f "$COORD" ]]; then
  echo "ERROR: coordination file not found: $COORD" >&2
  exit 1
fi

if [[ ! -f "$TASKS" ]]; then
  echo "ERROR: tasks file not found (change not active?): $TASKS" >&2
  exit 1
fi

need() {
  local label="$1" expected="$2"
  if ! rg -n "^- ${label}: ${expected}$" "$COORD" >/dev/null; then
    echo "ERROR: gate not satisfied: ${label} != ${expected} (in $COORD)" >&2
    exit 1
  fi
}

# --- Preflight (file gates + tasks) ---
need "PO" "done"
need "DEV" "done"
need "QA" "done"
need "Alan approval" "approved"
need "Alan homologation" "approved"

if rg -n "^- \[ \]" "$TASKS" >/dev/null; then
  echo "ERROR: tasks.md still has unchecked items" >&2
  rg -n "^- \[ \]" "$TASKS" | head -30 >&2
  exit 1
fi

# --- Preflight (Workflow DB must be reachable) ---
if ! curl -fsS "$WORKFLOW_HEALTH_URL" >/dev/null 2>&1; then
  echo "ERROR: workflow health unavailable at $WORKFLOW_HEALTH_URL" >&2
  echo "       (archiving is blocked because workflow DB is the source of truth)" >&2
  exit 2
fi

# Load backend/.env if present (WORKFLOW_DATABASE_URL, etc.)
if [[ -f backend/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source backend/.env
  set +a
fi

# --- Close coordination BEFORE archive (mirror/audit layer) ---
if rg -n "^- Alan homologation:" "$COORD" >/dev/null; then
  "$PY_BIN" - <<'PY' "$COORD"
from pathlib import Path
import sys
coord = Path(sys.argv[1])
md = coord.read_text(encoding='utf-8').splitlines()
out=[]
for line in md:
    if line.strip().lower().startswith('- alan homologation:'):
        out.append('- Alan homologation: approved')
    else:
        out.append(line)
text='\n'.join(out)+'\n'
if '## Closed' not in text:
    lines=text.splitlines()
    res=[]
    i=0
    inserted=False
    while i < len(lines):
        res.append(lines[i])
        if lines[i].strip()=='## Status':
            i+=1
            while i < len(lines) and not lines[i].strip().startswith('## '):
                res.append(lines[i]); i+=1
            res += ['', '## Closed', '', '- Homologated by Alan and archived.', '']
            inserted=True
            continue
        i+=1
    if not inserted:
        res += ['', '## Closed', '', '- Homologated by Alan and archived.', '']
    text='\n'.join(res)+'\n'
coord.write_text(text,encoding='utf-8')
PY
else
  echo "ERROR: coordination file missing 'Alan homologation' field" >&2
  exit 1
fi

git add "$COORD"
git commit -m "coordination: close ${CHANGE_ID} (homologation approved + Closed)" || true
git push origin main

# --- Atomic-ish archive transaction ---
# 1) Move workflow DB change to Archived (and ensure gates are approved in DB).
# 2) If OpenSpec archive fails, rollback workflow DB status.
PREV_STATUS=""
rollback_workflow_status() {
  local code=$?
  if [[ $code -ne 0 && -n "${PREV_STATUS}" ]]; then
    echo "WARN: archive failed; rolling back workflow status to '${PREV_STATUS}'" >&2
    WORKFLOW_DB_ENABLED=1 PYTHONPATH=backend \
      "$PY_BIN" backend/scripts/set_change_status.py \
        --project "$PROJECT_SLUG" --change "$CHANGE_ID" --status "$PREV_STATUS" >/dev/null 2>&1 || true
  fi
  exit $code
}
trap rollback_workflow_status EXIT

PREV_STATUS=$(
  WORKFLOW_DB_ENABLED=1 PYTHONPATH=backend \
    "$PY_BIN" backend/scripts/set_change_status.py \
      --project "$PROJECT_SLUG" --change "$CHANGE_ID" --status "Archived" \
      --approve-gates "PO,DEV,QA,Alan approval,Alan homologation" \
      --actor "archive_change_safe.sh"
)

# Archive in OpenSpec
openspec archive "$CHANGE_ID" --yes

git add -A
git commit -m "openspec: archive ${CHANGE_ID}" || true
git push origin main

# --- Mandatory post-archive validation (Kanban endpoint) ---
CHANGE_ID="$CHANGE_ID" KANBAN_URL="$KANBAN_URL" python3 - <<'PY'
import json, os, sys, urllib.request
change_id = os.environ.get('CHANGE_ID')
url = os.environ.get('KANBAN_URL')
if not change_id or not url:
    print('ERROR: missing CHANGE_ID/KANBAN_URL env', file=sys.stderr)
    sys.exit(2)
with urllib.request.urlopen(url, timeout=10) as r:
    data = json.loads(r.read().decode('utf-8'))
items = data.get('items') or []
item = next((it for it in items if it.get('id') == change_id), None)
if not item:
    print(f"ERROR: change '{change_id}' not found in Kanban endpoint after archive", file=sys.stderr)
    sys.exit(10)
if item.get('archived') is not True:
    print(f"ERROR: Kanban item archived!=true for '{change_id}': {item}", file=sys.stderr)
    sys.exit(11)
if (item.get('column') or '') != 'Archived':
    print(f"ERROR: Kanban item column!='Archived' for '{change_id}': {item}", file=sys.stderr)
    sys.exit(12)
print(f"OK: Kanban validated archived for {change_id}")
PY

# If we got here, do not rollback.
trap - EXIT

echo "OK: archived ${CHANGE_ID} safely (workflow DB + OpenSpec + Kanban validated)"
