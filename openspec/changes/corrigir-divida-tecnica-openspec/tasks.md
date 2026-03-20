## 1. Fix OpenSpec spec validation errors

- [ ] 1.1 Run `cd /root/.openclaw/workspace/crypto && openspec validate --specs` to identify all validation errors
- [ ] 1.2 Fix each of the 14 specs with validation errors: chart-visualization, combo-optimizer, combo-strategies, database-strategy-config, design, external-balances, favorites, optimization, optimization-engine, performance, performance-metrics, strategy-comparison, strategy-enablement, ui-ux
- [ ] 1.3 Add missing SHALL/MUST keywords per spec format
- [ ] 1.4 Add missing scenarios per spec format
- [ ] 1.5 Verify `openspec validate --specs` shows 0 errors (or document known/acknowledged issues)

## 2. Add health monitoring cron

- [ ] 2.1 Create health check script that verifies backend at http://127.0.0.1:8003/api/health returns 200
- [ ] 2.2 Create health check script that verifies frontend at http://127.0.0.1:5173 returns 200
- [ ] 2.3 Integrate Telegram notification to Alan on failure
- [ ] 2.4 Set up cron schedule for health checks (e.g., every 15 minutes)
- [ ] 2.5 Test health monitoring by simulating backend/frontend downtime

## 3. Fix or disable failing cron jobs

- [ ] 3.1 Investigate crypto-news-daily cron job errors (4 consecutive errors, likely rate limit)
- [ ] 3.2 Fix crypto-news-daily with exponential backoff OR disable and create manual trigger
- [ ] 3.3 Investigate monitor diario cron job errors (4 consecutive errors, likely rate limit)
- [ ] 3.4 Fix monitor diario with exponential backoff OR disable and create manual trigger
- [ ] 3.5 Verify cron jobs run without consecutive errors

## 4. Clean up legacy coordination docs

- [ ] 4.1 Review `docs/coordination/` directory contents
- [ ] 4.2 Identify archived/completed change files to remove
- [ ] 4.3 Remove archived files, keeping only README and active coordination files
- [ ] 4.4 Verify cleanup is complete
