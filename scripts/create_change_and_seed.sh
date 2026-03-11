#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 <change-name>" >&2
  exit 1
fi

CHANGE_NAME="$1"
PROJECT_SLUG="crypto"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OPENSPEC_DIR="openspec/changes/$CHANGE_NAME"
COORD_FILE="docs/coordination/$CHANGE_NAME.md"
WORKFLOW_HEALTH_URL="http://127.0.0.1:8003/api/workflow/health"
KANBAN_URL="http://127.0.0.1:8003/api/workflow/kanban/changes?project_slug=${PROJECT_SLUG}"

# 1) Create OpenSpec change if missing
if [ ! -d "$OPENSPEC_DIR" ]; then
  openspec new change "$CHANGE_NAME"
fi

# 2) Ensure coordination file exists (minimal bootstrap if missing)
if [ ! -f "$COORD_FILE" ]; then
  mkdir -p docs/coordination
  cat > "$COORD_FILE" <<EOF
# $CHANGE_NAME

## Status
- PO: in progress
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions (draft)
- Change created and awaiting PO elaboration.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/$CHANGE_NAME/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/$CHANGE_NAME/review-ptbr

## Notes
- Coordination card created automatically in the same turn as the change.

## Next actions
- [ ] PO: Elaborate proposal/spec/design/tasks.
EOF
fi

# 3) Seed workflow DB if workflow is enabled and reachable
if curl -fsS "$WORKFLOW_HEALTH_URL" >/dev/null 2>&1; then
  export PYTHONPATH=backend
  if [ -f backend/.env ]; then
    set -a
    source backend/.env
    set +a
  fi
  ./.venv/bin/python backend/scripts/seed_workflow_from_coordination.py --project "$PROJECT_SLUG"

  # 4) Verify change is visible in Kanban API
  if ! curl -fsS "$KANBAN_URL" | grep -q "$CHANGE_NAME"; then
    echo "ERRO: change '$CHANGE_NAME' não apareceu no Kanban após seed." >&2
    exit 2
  fi
else
  echo "Aviso: workflow health indisponível; change criada em OpenSpec + coordination, mas seed no DB não pôde ser validado agora." >&2
fi

echo "OK: change '$CHANGE_NAME' criada, coordination garantido e Kanban verificado."