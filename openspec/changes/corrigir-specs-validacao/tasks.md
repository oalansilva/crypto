## 1. Fix OpenSpec spec validation errors

- [ ] 1.1 Run `cd /root/.openclaw/workspace/crypto && openspec validate --specs 2>&1 | grep "✗"` to confirm the 11 failing specs
- [ ] 1.2 For each failing spec, open the spec file and add:
  - `## Purpose` section at the top (one sentence describing what the spec covers)
  - Missing `#### Scenario:` blocks with `**WHEN**` / `**THEN**` / `**AND**` format
  - Ensure every requirement line ends with SHALL/MUST
- [ ] 1.3 Verify: `openspec validate --specs 2>&1 | grep "✗"` returns 0 results
- [ ] 1.4 Commit: `git add openspec/specs/ && git commit -m "fix: corrigir validacao de specs openspec"`

## 2. Add health monitoring cron

- [ ] 2.1 Create health check script at `scripts/health_check.sh`:
  ```bash
  #!/bin/bash
  BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8003/api/health}"
  FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:5173}"
  ALAN_ID="${ALAN_ID:-555576937}"
  
  backend_ok=$(curl -sf "$BACKEND_URL" > /dev/null 2>&1 && echo ok || echo fail)
  frontend_ok=$(curl -sf "$FRONTEND_URL" > /dev/null 2>&1 && echo ok || echo fail)
  
  if [ "$backend_ok" != "ok" ] || [ "$frontend_ok" != "ok" ]; then
    MSG="⚠️ Health check falhou! "
    [ "$backend_ok" != "ok" ] && MSG="${MSG}Backend DOWN. "
    [ "$frontend_ok" != "ok" ] && MSG="${MSG}Frontend DOWN. "
    # Send via OpenClaw cron webhook or direct Telegram
    echo "$MSG"
  fi
  ```
- [ ] 2.2 Add OpenClaw cron: every 15 min, run health_check.sh, notify Alan on failure
- [ ] 2.3 Commit: `git add scripts/health_check.sh && git commit -m "feat: adicionar health monitoring cron"`

## 3. Fix or disable failing cron jobs

- [ ] 3.1 For crypto-news-daily and monitor diario: check current cron job config and error logs
- [ ] 3.2 Option A (preferred): add retry logic with backoff to the cron job scripts
- [ ] 3.2 Option B: disable both crons via `openclaw cron remove <job-id>`
- [ ] 3.3 Document decision in coordination file

## 4. Clean up docs/coordination

- [ ] 4.1 Run `ls docs/coordination/*.md` and identify files from archived changes
- [ ] 4.2 Remove archived coordination files (keep README.md)
- [ ] 4.3 Commit: `git add docs/coordination && git commit -m "chore: limpar docs/coordination de arquivos arquivados"`

## 5. Final verification and push

- [ ] 5.1 Run all tasks above
- [ ] 5.2 `git push origin main`
- [ ] 5.3 Register DEV approval and move to QA (see below)

## DEV → QA handoff commands

```bash
curl -s -X POST "http://127.0.0.1:8003/api/workflow/projects/crypto/changes/corrigir-specs-validacao/approvals" \
  -H "Content-Type: application/json" \
  -d '{"scope": "change", "gate": "DEV", "state": "approved", "actor": "DEV"}'

curl -s -X PATCH "http://127.0.0.1:8003/api/workflow/projects/crypto/changes/corrigir-specs-validacao" \
  -H "Content-Type: application/json" \
  -d '{"status": "QA"}'
```
