# Tasks: Manual Upstream Approval UI

**Change ID:** auto-upstream-completion

## Implementation Tasks

### Task 1: Create POST /upstream/approve endpoint (Backend)

**File:** `backend/app/routes/lab.py`  
**Location:** After `/upstream/message` endpoint (~line 800)

**Steps:**
1. Add the new endpoint:
   ```python
   @router.post("/runs/{run_id}/upstream/approve")
   async def approve_upstream(run_id: str):
       """Manual approval of upstream strategy_draft by user."""
       run_state = _load_run(run_id)
       if not run_state:
           raise HTTPException(status_code=404, detail="Run not found")
       
       upstream = run_state.get("upstream", {})
       
       # Validate preconditions
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
       
       # Transition status
       run_state["status"] = "ready_for_execution"
       
       # Save
       _save_run(run_id, run_state)
       
       logger.info(f"[{run_id}] Upstream approved by user")
       
       return run_state
   ```

2. Verify imports (already should exist):
   - `from fastapi import HTTPException`
   - `import time`
   - `import logging; logger = logging.getLogger(__name__)`

3. Test endpoint manually with curl:
   ```bash
   curl -X POST http://localhost:8003/api/lab/runs/c4079c1d109b45c09a8b350788b9218b/upstream/approve
   ```

**Acceptance:**
- Endpoint returns 200 with updated run state
- `user_approved` is set to `true`
- Event `upstream_approved` logged in `.jsonl` file
- Status transitions to `ready_for_execution`

---

### Task 2: Add approval button to frontend (UI)

**File:** `frontend/src/pages/LabRunDetail.tsx`  
**Location:** In the upstream section, after `strategy_draft` display

**Steps:**

1. Add state for button loading:
   ```typescript
   const [approving, setApproving] = useState(false);
   ```

2. Add approval handler function:
   ```typescript
   const handleApproveUpstream = async () => {
     if (!run) return;
     setApproving(true);
     try {
       const response = await axios.post(
         `/api/lab/runs/${run.run_id}/upstream/approve`
       );
       setRun(response.data);
       // Optional: show success toast
       console.log('Upstream approved successfully');
     } catch (error: any) {
       console.error('Approval failed:', error);
       const msg = error.response?.data?.detail || 'Failed to approve';
       alert(msg);
     } finally {
       setApproving(false);
     }
   };
   ```

3. Add conditional button render in JSX:
   ```tsx
   {run.upstream?.ready_for_user_review && !run.upstream?.user_approved && (
     <div className="approve-upstream-section">
       <button
         onClick={handleApproveUpstream}
         disabled={approving}
         className="btn btn-primary approve-upstream-btn"
       >
         {approving ? 'Aprovando...' : 'Aprovar Upstream'}
       </button>
       <p className="help-text">
         Ao aprovar, a estratégia será enviada para análise (Dev → Validator → Trader).
       </p>
     </div>
   )}
   
   {run.upstream?.user_approved && (
     <div className="upstream-approved-badge">
       ✅ Upstream aprovado — Análise em andamento
     </div>
   )}
   ```

4. Add CSS styles (create or append to `LabRunDetail.css` or inline styles):
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
   ```

**Acceptance:**
- Button appears when `ready_for_user_review=true` and `user_approved=false`
- Clicking button shows "Aprovando..." loading state
- After approval, button disappears and "Aprovado" badge appears
- Run state updates in UI automatically

---

### Task 3: Test full flow (Backend + Frontend)

**Manual test:**
1. Restart backend: `systemctl restart crypto-backend.service`
2. Restart frontend: `systemctl restart crypto-frontend.service`
3. Open UI: http://31.97.92.212:5173/lab
4. Create new run:
   - Objective: "quero uma estrategia em BTC"
   - Answer Trader: "BTC/USDT" → "4h"
5. Wait for Trader to generate `strategy_draft`
6. **Verify:**
   - "Aprovar Upstream" button appears
   - `strategy_draft` content is visible
7. Click "Aprovar Upstream"
8. **Verify:**
   - Button shows "Aprovando..." (disabled)
   - After ~1s, success
   - Button disappears, "Aprovado" badge appears
   - Status changes to `ready_for_execution`
   - Personas start executing (coordinator → dev → ...)

**Check backend logs:**
```bash
journalctl -u crypto-backend.service -n 50 | grep "approved"
```

Expected: `[{run_id}] Upstream approved by user`

**Check event log:**
```bash
cat backend/logs/lab_runs/{run_id}.jsonl | grep upstream_approved
```

Expected: Single `upstream_approved` event with inputs

**Acceptance:**
- End-to-end flow works
- No errors in browser console or backend logs
- Run progresses through all phases

---

### Task 4: Test retroactive approval (old run)

**Manual test:**
1. Load old run `c4079c1d109b45c09a8b350788b9218b` in UI
2. **Verify:** "Aprovar Upstream" button appears (retroactive fix)
3. Click button
4. **Verify:** Run transitions to `ready_for_execution`
5. **Verify:** Personas start executing

**Acceptance:**
- Old stuck runs can be approved and resumed
- No breaking changes for existing data

---

### Task 5: Test duplicate approval prevention

**Manual test:**
1. Use run from Task 3 (already approved)
2. Reload page
3. **Verify:** Button does NOT appear (already approved badge shown)
4. Manually call API via curl:
   ```bash
   curl -X POST http://localhost:8003/api/lab/runs/{run_id}/upstream/approve
   ```
5. **Verify:** HTTP 400 response with `{"detail": "Already approved"}`
6. **Verify:** Event log shows only ONE `upstream_approved` event (no duplicate)

**Acceptance:**
- Idempotency guard works
- No duplicate events
- Clear error message for duplicate attempts

---

### Task 6: Commit and deploy

**Steps:**
1. Switch to `feature/long-change` branch:
   ```bash
   cd /root/.openclaw/workspace/crypto
   git checkout feature/long-change
   ```

2. Stage changes:
   ```bash
   git add backend/app/routes/lab.py
   git add frontend/src/pages/LabRunDetail.tsx
   git add frontend/src/pages/LabRunDetail.css  # if created
   git add openspec/changes/auto-upstream-completion/
   ```

3. Commit:
   ```bash
   git commit -m "feat: add manual upstream approval UI (fixes stuck ready_for_review runs)

- Add POST /upstream/approve endpoint
- Add 'Aprovar Upstream' button in UI when ready_for_user_review=true
- Emit upstream_approved event on manual approval
- Transition status ready_for_review -> ready_for_execution
- Prevent duplicate approvals with 400 error
- Works retroactively for old stuck runs

Closes: auto-upstream-completion change proposal"
   ```

4. Push:
   ```bash
   git push origin feature/long-change
   ```

5. Restart services on VPS:
   ```bash
   systemctl restart crypto-backend.service
   systemctl restart crypto-frontend.service
   ```

6. Verify in production:
   - Open http://31.97.92.212:5173/lab
   - Test with new run

**Acceptance:**
- Code pushed to `feature/long-change`
- Services restarted
- Feature works in production

---

## Completion Checklist

- [ ] Task 1: Backend endpoint created and tested
- [ ] Task 2: Frontend button and handler implemented
- [ ] Task 3: Full flow tested (new run)
- [ ] Task 4: Retroactive approval tested (old run c4079c1d...)
- [ ] Task 5: Duplicate prevention verified
- [ ] Task 6: Code committed and deployed to VPS
- [ ] UI tested in production (http://31.97.92.212:5173)
- [ ] Change proposal archived with evidence (commit hash + tested URL)

---

## Rollback Procedure

If critical issues occur:
1. Identify commit: `git log -1 --oneline`
2. Revert: `git revert <hash>`
3. Push: `git push origin feature/long-change`
4. Restart: `systemctl restart crypto-backend.service crypto-frontend.service`
5. Verify: Old behavior restored, stuck runs remain in `ready_for_review`
