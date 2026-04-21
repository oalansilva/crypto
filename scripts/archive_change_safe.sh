#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <change-id>" >&2
  exit 1
fi

CHANGE_ID="$1"
PROJECT_SLUG="${PROJECT_SLUG:-crypto}"
WORKFLOW_BASE_URL="${WORKFLOW_BASE_URL:-http://127.0.0.1:8003}"
WORKFLOW_HEALTH_URL="${WORKFLOW_HEALTH_URL:-$WORKFLOW_BASE_URL/api/workflow/health}"
KANBAN_URL="${KANBAN_URL:-$WORKFLOW_BASE_URL/api/workflow/kanban/changes?project_slug=${PROJECT_SLUG}}"

cd "$(dirname "$0")/.."

TASKS="openspec/changes/${CHANGE_ID}/tasks.md"
PY_BIN="./backend/.venv/bin/python"
if [[ ! -x "$PY_BIN" ]]; then
  PY_BIN="python3"
fi

if [[ ! -f "$TASKS" ]]; then
  echo "ERROR: tasks file not found: $TASKS" >&2
  exit 1
fi

# --- Preflight (workflow runtime + tasks) ---
if rg -n "^- \[ \]" "$TASKS" >/dev/null; then
  echo "ERROR: tasks.md ainda tem itens não concluídos" >&2
  rg -n "^- \[ \]" "$TASKS" | head -30 >&2
  exit 1
fi

if ! curl -fsS "$WORKFLOW_HEALTH_URL" >/dev/null 2>&1; then
  echo "ERROR: workflow DB indisponível em $WORKFLOW_HEALTH_URL" >&2
  echo "       (arquivo de archive bloqueado enquanto o backend/runtime não responde)." >&2
  exit 2
fi

if ! ./scripts/verify_upstream_published.py --for-status "Archived"; then
  echo "ERROR: upstream guard bloqueou archive; envie mudanças para o GitHub antes de arquivar." >&2
  exit 1
fi

if [[ -f backend/.env ]]; then
  set -a
  # shellcheck disable=SC1091
  source backend/.env
  set +a
fi

# --- Atualiza Workflow DB para estado final e fecha portas obrigatórias ---
PREV_STATUS=""
ARCHIVE_COMMITTED=0
rollback_workflow_status() {
  local code=$?
  if [[ $code -ne 0 && -n "${PREV_STATUS}" && $ARCHIVE_COMMITTED -eq 0 ]]; then
    echo "WARN: falha antes de concluir OpenSpec archive; revertendo status para '${PREV_STATUS}'..." >&2
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
      --approve-gates "PO,DEV,QA,Alan approval,Homologation" \
      --actor "archive_change_safe.sh"
)

# --- Arquiva no OpenSpec ---
"$PY_BIN" ./backend/scripts/reconcile_openspec_change_headers.py "$CHANGE_ID"
openspec archive "$CHANGE_ID" --yes

ARCHIVE_COMMITTED=1
OPEN_SPEC_ARCHIVE_DIR=""
for candidate in openspec/changes/archive/*; do
  [[ -d "$candidate" ]] || continue
  if [[ "$(basename "$candidate")" == *"$CHANGE_ID"* ]]; then
    OPEN_SPEC_ARCHIVE_DIR="$candidate"
    break
  fi
done

if [[ -z "$OPEN_SPEC_ARCHIVE_DIR" || -d "openspec/changes/$CHANGE_ID" ]]; then
  echo "ERROR: arquivo OpenSpec não foi movido para archive para '$CHANGE_ID'." >&2
  exit 1
fi

git add -A
git commit -m "openspec: archive ${CHANGE_ID}" || true
git push origin main

# --- Validação rápida no endpoint de runtime (sem rollback do DB) ---
CHANGE_ID="$CHANGE_ID" KANBAN_URL="$KANBAN_URL" python3 - <<'PY'
import json, os, sys, time, urllib.request

change_id = os.environ.get("CHANGE_ID")
url = os.environ.get("KANBAN_URL")
if not change_id or not url:
    print("ERROR: variáveis CHANGE_ID/KANBAN_URL ausentes", file=sys.stderr)
    sys.exit(2)

attempts = int(os.environ.get("KANBAN_VALIDATE_ATTEMPTS", "6"))
base_sleep = float(os.environ.get("KANBAN_VALIDATE_BASE_SLEEP_S", "1.0"))
base_timeout = float(os.environ.get("KANBAN_VALIDATE_TIMEOUT_S", "15"))

last_err = None
for i in range(1, attempts + 1):
    timeout = base_timeout * (1.5 ** (i - 1))
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        items = data.get("items") or []
        item = next((it for it in items if it.get("id") == change_id), None)
        if not item:
            raise RuntimeError(f"change '{change_id}' não encontrada em /api/workflow/kanban/changes")
        if item.get("archived") is not True:
            raise RuntimeError(f"kanban.archived != true: {item}")
        if (item.get("column") or "") != "Archived":
            raise RuntimeError(f"kanban.column != Archived: {item}")
        print(f"OK: archive validado no Kanban (attempt {i}/{attempts}, timeout={timeout:.1f}s)")
        sys.exit(0)
    except Exception as e:
        last_err = e
        if i < attempts:
            sleep_s = base_sleep * (2 ** (i - 1))
            print(
                f"WARN: tentativa {i}/{attempts} falhou: {e}; nova tentativa em {sleep_s:.1f}s (timeout {timeout:.1f}s)",
                file=sys.stderr,
            )
            time.sleep(sleep_s)

print("ERROR: pós-arquivo não validado no Kanban após retries.", file=sys.stderr)
print(f"       Isso não desfaz o status de workflow DB (OpenSpec já está em archive).", file=sys.stderr)
print(f"       Último erro: {last_err}", file=sys.stderr)
sys.exit(50)
PY

trap - EXIT

echo "OK: archived com sucesso ${CHANGE_ID} (Workflow DB + OpenSpec + Kanban validado)"
