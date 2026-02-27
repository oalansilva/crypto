#!/usr/bin/env bash
set -euo pipefail

CHANGE_ID="$1"

cd "$(dirname "$0")/.."

COORD="docs/coordination/${CHANGE_ID}.md"
TASKS="openspec/changes/${CHANGE_ID}/tasks.md"

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

# Validate gates before closing
need "PO" "done"
need "DEV" "done"
need "QA" "done"
need "Alan approval" "approved"

# Ensure tasks are all checked
if rg -n "^- \[ \]" "$TASKS" >/dev/null; then
  echo "ERROR: tasks.md still has unchecked items" >&2
  rg -n "^- \[ \]" "$TASKS" | head -30 >&2
  exit 1
fi

# Close coordination (homologation + Closed section) BEFORE archive
if rg -n "^- Alan homologation:" "$COORD" >/dev/null; then
  # replace the line
  python3 - <<PY
from pathlib import Path
p=Path("$COORD")
md=p.read_text(encoding='utf-8').splitlines()
out=[]
for line in md:
    if line.strip().lower().startswith('- alan homologation:'):
        out.append('- Alan homologation: approved')
    else:
        out.append(line)
text='\n'.join(out)+'\n'
if '## Closed' not in text:
    # insert after Status section
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

p.write_text(text,encoding='utf-8')
PY
else
  echo "ERROR: coordination file missing 'Alan homologation' field" >&2
  exit 1
fi

# Commit coordination closure
git add "$COORD"
git commit -m "coordination: close ${CHANGE_ID} (homologation approved + Closed)" || true
git push origin main

# Archive
openspec archive "$CHANGE_ID" --yes

git add -A
git commit -m "openspec: archive ${CHANGE_ID}" || true
git push origin main

echo "OK: archived ${CHANGE_ID} safely"
