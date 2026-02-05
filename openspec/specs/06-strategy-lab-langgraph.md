---
spec: openspec.v1
id: crypto.lab.langgraph.v1
title: Strategy Lab (LangGraph) with 3 personas + autosave templates/favorites
status: draft
owner: Alan
created_at: 2026-02-05
updated_at: 2026-02-05
---

# 0) One-liner

Add a new "Strategy Lab" feature (new UI + backend endpoints) that runs a LangGraph workflow with 3 personas (Coordinator, Dev Senior, Trader Validator) to generate/improve strategies using existing templates, run backtests, and **auto-save** the resulting combo_template + favorite.

# 1) Context

- Current system already supports:
  - combo_templates (templates)
  - backtesting
  - favorites
  - agent chat about favorites
- We want a more structured workflow where multiple personas collaborate and use the existing tools to create new templates/strategies.
- We want to avoid breaking the current app: this must be a separate feature/tela.

# 2) Goal

## In scope
- New UI page: `/lab`
- Backend endpoints to:
  - create a "lab run" request
  - execute a LangGraph flow in-process (FastAPI backend)
  - persist results:
    - auto-save a combo_template (new name)
    - auto-save a FavoriteStrategy linked to the run
- Three personas (LLM prompts/roles):
  1) Coordinator: orchestration + final decision
  2) Dev Senior: template changes + implementation notes
  3) Trader Validator: risk/robustness checks + approve/reject
- Tooling inside the graph:
  - read available templates
  - propose template modifications (declarative)
  - run backtest using existing backtest engine
  - save template + favorite

## Out of scope (v1)
- Creating brand-new Python strategy classes (only modify/use templates)
- Multi-tenant auth
- Advanced optimization (grid/BO) beyond a small candidate set
- Long-running job queue + progress streaming (we can do synchronous MVP first)

# 3) User stories

- As Alan, I want to describe an objective (symbol/timeframe/constraints) and let the system propose + validate a strategy.
- As Alan, I want the system to automatically save the winning template and favorite so I can review it in Favorites.

# 4) UX / UI

## Route: `/lab`

- Inputs:
  - Symbol (dropdown)
  - Timeframe
  - Base template (dropdown)
  - Constraints (max DD, min Sharpe, direction, etc.)
  - Optional free-text objective
- Actions:
  - "Run Lab" button
- Outputs:
  - Summary from Coordinator
  - Validator verdict (approved/rejected + reasons)
  - Links:
    - Open saved Favorite
    - Open saved Template (edit screen)

States:
- Loading (graph running)
- Error
- Success (show saved ids)

# 5) API / Contracts

## Backend

### POST /api/lab/run
Request:
```json
{
  "symbol": "SOL/USDT",
  "timeframe": "1d",
  "base_template": "multi_ma_crossover",
  "direction": "long",
  "constraints": {
    "max_drawdown": 0.20,
    "min_sharpe": 0.4
  },
  "objective": "Gerar uma versão mais robusta para bear",
  "thinking": "low"
}
```

Response (success):
```json
{
  "run_id": "...",
  "status": "ok",
  "coordinator_summary": "...",
  "validator": { "verdict": "approved", "notes": "..." },
  "dev": { "changes": "..." },
  "saved": {
    "template_name": "lab_multi_ma_crossover_sol_1d_20260205",
    "favorite_id": 123
  },
  "backtest": {
    "metrics": { "sharpe_ratio": 0.5, "max_drawdown": 0.18 }
  }
}
```

Response (error):
- 4xx validation errors
- 5xx execution errors

## OpenClaw / LLM
- Use OpenClaw Gateway agent (same OAuth) similarly to agent chat.
- Personas implemented as distinct system prompts and tool-selection instructions.

# 6) Data model changes

- Optional (v1): a new DB table `lab_runs` to persist:
  - inputs
  - graph outputs
  - created template name
  - created favorite id
  - timestamps

If we skip DB in v1, at least return ids and rely on existing tables.

# 7) VALIDATE (mandatory)

## Proposal link

- Proposal URL: http://31.97.92.212:5173/openspec/06-strategy-lab-langgraph
- Status: draft → validated → approved → implemented

Before implementation, complete this checklist:

- [ ] Scope is unambiguous (in-scope/out-of-scope are explicit)
- [ ] Acceptance criteria are testable (binary pass/fail)
- [ ] API/contracts are specified (request/response/error) when applicable
- [ ] UX states covered (loading/empty/error)
- [ ] Security considerations noted (auth/exposure) when applicable
- [ ] Test plan includes manual smoke + at least one automated check
- [ ] Open questions resolved or explicitly tracked

# 8) Acceptance criteria (Definition of Done)

- [ ] `/lab` page exists and can trigger a lab run.
- [ ] A lab run produces:
  - a backtest result
  - a coordinator summary
  - a validator verdict
  - a dev change summary
- [ ] On success, system auto-saves:
  - a new combo_template
  - a new favorite strategy
- [ ] Saved favorite is visible on `/favorites` and can be opened in Agent chat.
- [ ] No regressions on existing routes (`/favorites`, `/combo/*`).

# 9) Test plan

## Manual smoke
1. Open `/lab`
2. Run with base template `multi_ma_crossover` on `BTC/USDT 1d`
3. Confirm run returns approved/rejected with summary
4. Confirm new favorite appears in `/favorites`

## Automated
- Backend: unit test for request validation + safe template naming
- Frontend: `npm run build`

# 10) Rollout / rollback

- Rollout: deploy backend+frontend, feature available at `/lab`
- Rollback: revert to git tag `stable-2026-02-05`

# 11) USER TEST (mandatory)

After deployment/restart, Alan will validate in the UI.

- Test URL(s):
  - http://31.97.92.212:5173/lab
- What to test (smoke steps):
  1) Run a lab task and verify it auto-saves.
  2) Confirm the saved favorite exists and agent chat works.
- Result:
  - [ ] Alan confirmed: OK

# 12) ARCHIVE / CLOSE (mandatory)

Only after Alan confirms OK:

- [ ] Update spec frontmatter `status: implemented`
- [ ] Update `updated_at`
- [ ] Add brief evidence (commit hash + URL tested) in the spec

# 13) Notes / open questions

- Do we need async jobs for long runs (queue/progress) in v1, or is sync acceptable?
- Naming convention for auto-saved templates/favorites (format + uniqueness)
- Candidate generation: how many variants per run? (default: 3-5)
