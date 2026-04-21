#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 <change-name>" >&2
  exit 1
fi

CHANGE_NAME="$1"
PROJECT_SLUG="${PROJECT_SLUG:-crypto}"
WORKFLOW_BASE_URL="${WORKFLOW_BASE_URL:-http://127.0.0.1:8003}"
WORKFLOW_HEALTH_URL="${WORKFLOW_HEALTH_URL:-$WORKFLOW_BASE_URL/api/workflow/health}"
KANBAN_URL="${KANBAN_URL:-$WORKFLOW_BASE_URL/api/workflow/kanban/changes?project_slug=${PROJECT_SLUG}}"
KANBAN_CREATE_URL="${WORKFLOW_BASE_URL}/api/workflow/kanban/changes?project_slug=${PROJECT_SLUG}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OPENSPEC_DIR="openspec/changes/$CHANGE_NAME"
TASKS="openspec/changes/$CHANGE_NAME/tasks.md"

# 1) Garante a change no OpenSpec
if [ ! -d "$OPENSPEC_DIR" ]; then
  openspec new change "$CHANGE_NAME"
fi

if [ ! -f "$TASKS" ]; then
  echo "WARN: tasks.md ainda não existe. Crie pelo assistente OpenSpec antes de avançar."
fi

# 2) Opcional: registra change no Workflow DB se o backend estiver no ar
if curl -fsS "$WORKFLOW_HEALTH_URL" >/dev/null 2>&1; then
  echo "Backend workflow disponível; garantindo entrada do card no banco..."
  if ! curl -fsS "$KANBAN_URL" | grep -q "\"id\":\"${CHANGE_NAME}\""; then
    CREATE_PAYLOAD='{"title": "'"${CHANGE_NAME}"'", "description": "OpenSpec change bootstrap by create_change_and_seed.sh"}'
    if ! HTTP_STATUS=$(curl -sS -o /tmp/create_change_http_response.json -w "%{http_code}" -H "Content-Type: application/json" -X POST -d "$CREATE_PAYLOAD" "$KANBAN_CREATE_URL"); then
      echo "WARN: falha ao tentar criar card no workflow DB (HTTP request)." >&2
    elif [[ "$HTTP_STATUS" != 2* ]]; then
      echo "WARN: criação via workflow retornou HTTP ${HTTP_STATUS}. Verifique logs do backend." >&2
      cat /tmp/create_change_http_response.json >&2 || true
    else
      echo "OK: card criado no workflow DB."
    fi
  else
    echo "OK: change já existe no workflow DB."
  fi
else
  echo "Aviso: backend indisponível, change criada no OpenSpec apenas."
fi

echo "OK: change '$CHANGE_NAME' preparada."
