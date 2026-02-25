# Design: Manual Upstream Approval UI

**Change ID:** auto-upstream-completion

## Overview: Upstream as Conversational Brainstorm

The **upstream phase** is a **conversational brainstorm** between the **Trader persona** (LLM) and the **human user**:

1. **Trader asks questions** to gather inputs (symbol, timeframe, objective, constraints)
2. **User responds** in natural language (no rigid format required)
3. **Iterative refinement:** User can ask Trader to adjust ideas, add indicators, change thresholds
4. **Draft generation:** When Trader has sufficient info, generates a `strategy_draft` and marks `ready_for_user_review: true`
5. **User decision:** 
   - **Approve** → Click button → Progresses to Dev/Validator/Trader phases
   - **Refine** → Send more messages to Trader → Update draft iteratively

**Key insight:** The "Approve Upstream" button does NOT force immediate approval — it's an **option available when the user is satisfied**. The conversation can continue indefinitely until the user decides to approve.

---

## Architecture

### Component Overview

```
┌───────────────────────────────────────────────────────────────┐
│                    Frontend (LabRunDetail)                     │
│  - Display strategy_draft when ready_for_user_review=true     │
│  - Show "Approve Upstream" button                             │
│  - onClick → POST /upstream/approve                           │
└─────────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────────────────┐
    │   POST /api/lab/runs/{run_id}/upstream/approve          │
    │   (backend/app/routes/lab.py, novo endpoint)            │
    └─────────────────────┬───────────────────────────────────┘
                          │
                          ├─► Validate state
                          │   └─► ready_for_user_review=true?
                          │       user_approved=false?
                          │
                          ├─► Update upstream state
                          │   ├─► upstream["user_approved"] = true
                          │   └─► Emit event: upstream_approved
                          │
                          └─► Return updated run
                              └─► status: ready_for_execution
```

### State Transition Diagram

```
┌─────────────────┐
│  needs_user_    │  User sends messages
│     input       │─────────────────┐
└─────────────────┘                 │
                                    ▼
                         ┌─────────────────────┐
                         │   Trader responds    │
                         │ (gather inputs)      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
        contract.missing != []       contract.missing == []
        ready_for_review=false       ready_for_review=true
                    │                                │
                    ▼                                ▼
        ┌─────────────────┐            ┌─────────────────────┐
        │  needs_user_    │            │ ready_for_review    │
        │     input       │            │ (WAITING FOR USER)  │
        └─────────────────┘            └──────────┬───────────┘
                                                  │
                                                  │ User clicks
                                                  │ "Approve Upstream"
                                                  ▼
                                       ┌─────────────────────┐
                                       │ POST /upstream/     │
                                       │      approve        │
                                       └──────────┬───────────┘
                                                  │
                                                  ▼
                                       ┌─────────────────────┐
                                       │ ready_for_execution │
                                       │ (user_approved=true)│
                                       └──────────┬───────────┘
                                                  │
                                                  │ Auto-trigger
                                                  ▼
                                       ┌─────────────────────┐
                                       │   decision phase    │
                                       │ (coordinator→dev→   │
                                       │  validator→trader)  │
                                       └─────────────────────┘
```

### Data Flow

**Frontend:**
```typescript
// LabRunDetail.tsx
const handleApproveUpstream = async () => {
  setApproving(true);
  try {
    const response = await axios.post(
      `/api/lab/runs/${runId}/upstream/approve`
    );
    setRun(response.data); // Update local state
    // UI will automatically update to show next phase
  } catch (error) {
    console.error('Approval failed:', error);
    alert(error.response?.data?.detail || 'Failed to approve');
  } finally {
    setApproving(false);
  }
};

// Render button conditionally
{run.upstream.ready_for_user_review && !run.upstream.user_approved && (
  <button
    onClick={handleApproveUpstream}
    disabled={approving}
    className="approve-upstream-btn"
  >
    {approving ? 'Aprovando...' : 'Aprovar Upstream'}
  </button>
)}
```

**Backend:**
```python
# backend/app/routes/lab.py
@router.post("/runs/{run_id}/upstream/approve")
async def approve_upstream(run_id: str):
    """
    Manual approval of upstream strategy_draft by user.
    Transitions run from ready_for_review → ready_for_execution.
    """
    # Load run
    run_state = _load_run(run_id)
    upstream = run_state.get("upstream", {})
    
    # Validate preconditions
    if not bool(upstream.get("ready_for_user_review")):
        raise HTTPException(
            status_code=400,
            detail="Cannot approve: Trader has not marked ready_for_user_review"
        )
    
    if bool(upstream.get("user_approved")):
        raise HTTPException(
            status_code=400,
            detail="Already approved"
        )
    
    # Approve
    upstream["user_approved"] = True
    run_state["updated_at_ms"] = int(time.time() * 1000)
    
    # Emit event
    contract = run_state.get("upstream_contract", {})
    _emit_event(run_id, "upstream_approved", {
        "inputs": contract.get("inputs", {})
    })
    
    # Update status
    run_state["status"] = "ready_for_execution"
    
    # Save
    _save_run(run_id, run_state)
    
    logger.info(f"[{run_id}] Upstream manually approved by user")
    
    return run_state
```

## Components Modified

### 1. Backend: `app/routes/lab.py`

**New endpoint:** `POST /api/lab/runs/{run_id}/upstream/approve`

**Location:** Add after existing `/upstream/message` endpoint (around line ~800)

**Implementation:**
```python
@router.post("/runs/{run_id}/upstream/approve")
async def approve_upstream(run_id: str):
    """
    Manual approval endpoint for upstream strategy_draft.
    User must explicitly approve before personas execute.
    """
    run_state = _load_run(run_id)
    if not run_state:
        raise HTTPException(status_code=404, detail="Run not found")
    
    upstream = run_state.get("upstream", {})
    
    # Precondition checks
    if not bool(upstream.get("ready_for_user_review")):
        raise HTTPException(400, "Cannot approve: not ready for review")
    
    if bool(upstream.get("user_approved")):
        raise HTTPException(400, "Already approved")
    
    # Approve
    upstream["user_approved"] = True
    run_state["updated_at_ms"] = int(time.time() * 1000)
    
    # Emit event
    contract = run_state.get("upstream_contract", {})
    _emit_event(run_id, "upstream_approved", {
        "inputs": contract.get("inputs", {})
    })
    
    # Status transition
    run_state["status"] = "ready_for_execution"
    
    # Save
    _save_run(run_id, run_state)
    
    logger.info(f"[{run_id}] Upstream approved by user")
    
    return run_state
```

**Helpers used:**
- `_load_run(run_id)` — already exists
- `_save_run(run_id, state)` — already exists
- `_emit_event(run_id, type, payload)` — already exists
- `logger` — already imported

---

### 2. Frontend: `frontend/src/pages/LabRunDetail.tsx`

**Location:** In the upstream chat section, after displaying `strategy_draft`

**New state:**
```typescript
const [approving, setApproving] = useState(false);
```

**New handler:**
```typescript
const handleApproveUpstream = async () => {
  if (!run) return;
  setApproving(true);
  try {
    const response = await axios.post(
      `/api/lab/runs/${run.run_id}/upstream/approve`
    );
    setRun(response.data); // Update local run state
    toast.success('Upstream aprovado! Iniciando análise...');
  } catch (error: any) {
    console.error('Approval failed:', error);
    const msg = error.response?.data?.detail || 'Falha ao aprovar';
    toast.error(msg);
  } finally {
    setApproving(false);
  }
};
```

**Render button:**
```tsx
{/* Show approve button when ready for review and not yet approved */}
{run.upstream?.ready_for_user_review && !run.upstream?.user_approved && (
  <div className="approve-upstream-section">
    <button
      onClick={handleApproveUpstream}
      disabled={approving}
      className="btn btn-primary approve-upstream-btn"
    >
      {approving ? (
        <>
          <span className="spinner-small" />
          Aprovando...
        </>
      ) : (
        'Aprovar Upstream'
      )}
    </button>
    <p className="help-text">
      Ao aprovar, a estratégia será enviada para Dev, Validator e Trader.
    </p>
  </div>
)}

{/* Show status when already approved */}
{run.upstream?.user_approved && (
  <div className="upstream-approved-badge">
    ✅ Upstream aprovado — Análise em andamento
  </div>
)}
```

**Styling (add to LabRunDetail.css):**
```css
.approve-upstream-section {
  margin-top: 1.5rem;
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  text-align: center;
}

.approve-upstream-btn {
  background: #4caf50;
  color: white;
  padding: 0.75rem 2rem;
  font-size: 1rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.approve-upstream-btn:hover:not(:disabled) {
  background: #45a049;
}

.approve-upstream-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.help-text {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.upstream-approved-badge {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 8px;
  font-weight: 500;
}

.spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## Edge Cases

| Case | Handling |
|------|----------|
| User clicks approve multiple times quickly | `setApproving(true)` disables button during request; backend returns 400 if already approved |
| Network error during approval | Frontend shows error toast; user can retry |
| Run state changes while user reviews draft | Next poll will update UI; if already approved elsewhere, button disappears |
| Old run stuck in `ready_for_review` | Button will appear retroactively (works for all runs with `ready_for_user_review=true && user_approved=false`) |

## Testing Plan

### Manual Tests

**Test 1: Happy path**
1. Create new run: "quero uma estrategia em BTC"
2. Respond: "BTC/USDT" → "4h"
3. Wait for Trader to generate `strategy_draft`
4. **Verify:** "Aprovar Upstream" button appears
5. **Verify:** `strategy_draft` content is visible above button
6. Click "Aprovar Upstream"
7. **Verify:** Button shows "Aprovando..." (disabled)
8. **Verify:** After success, status → `ready_for_execution`
9. **Verify:** Event `upstream_approved` logged
10. **Verify:** Personas start executing

**Test 2: Duplicate approval prevention**
1. Use run from Test 1 (already approved)
2. Manually call `POST /upstream/approve` via curl or Postman
3. **Verify:** HTTP 400 response with "Already approved"
4. **Verify:** No duplicate `upstream_approved` event

**Test 3: Button does not appear when not ready**
1. Create new run, send first message
2. **Verify:** Button does NOT appear (Trader still gathering inputs)
3. Complete inputs
4. **Verify:** Button appears only when `ready_for_user_review=true`

**Test 4: Retroactive approval (old run)**
1. Load run `c4079c1d109b45c09a8b350788b9218b` (stuck in `ready_for_review`)
2. **Verify:** Button appears
3. Click approve
4. **Verify:** Run progresses to `ready_for_execution`

---

## Migration Strategy

**No migration needed** — the feature works retroactively:
- Old runs with `ready_for_review` + `ready_for_user_review=true` will automatically show the approval button
- User can approve them on-demand
- No database schema changes required

---

## Rollback Plan

If issues occur:
1. Revert commit: `git revert <hash>`
2. Push: `git push origin feature/long-change`
3. Restart backend: `systemctl restart crypto-backend.service`
4. Restart frontend: `systemctl restart crypto-frontend.service`
5. Runs remain in `ready_for_review` state (no data corruption)

**Low risk:** Change only adds new endpoint + UI element; doesn't modify existing flows.
