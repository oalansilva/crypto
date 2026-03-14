# Tasks — evolve-multiagent-kadro-operating-model

## Phase 1 — Standardize the operating model

### 1. Agent role contract
- [x] 1.1 Define explicit responsibilities for `main`, `PO`, `DESIGN`, `DEV`, and `QA`. Superseded: delivered in `standardize-multiagent-kadro-operating-model`.
- [x] 1.2 Define what each role must update before claiming a stage is complete. Superseded: delivered in `standardize-multiagent-kadro-operating-model`.
- [x] 1.3 Define what each role must **not** do (for example, main should not absorb heavy technical execution by default). Superseded: delivered in `standardize-multiagent-kadro-operating-model`.

### 2. Handoff standardization
- [x] 2.1 Define the standard Kanban handoff/comment template.
- [x] 2.2 Provide per-role examples for PO, DESIGN, DEV, and QA handoffs.
- [x] 2.3 Define the minimum evidence expected in a handoff.

### 3. Definition of Done by stage
- [x] 3.1 Define Definition of Done for `Pending`, `PO`, `DESIGN`, `Alan approval`, `DEV`, `QA`, `Alan homologation`, and `Archived`.
- [x] 3.2 Define the rule that a stage is only complete when runtime state and handoff comment are both updated.
- [x] 3.3 Define stage-specific failure / blocked-state expectations when a handoff cannot proceed.

### 4. Legacy coordination demotion
- [x] 4.1 Define `docs/coordination/*.md` as mirror/audit only, not active operational truth.
- [x] 4.2 Define how agents should behave when legacy coordination and runtime differ.
- [x] 4.3 Update the documented operational model so the Kanban/workflow DB is the primary execution surface.

### 5. Playbook consolidation
- [x] 5.1 Consolidate the Phase 1 rules into a single operational playbook.
- [x] 5.2 Make sure the playbook is short enough to be used consistently.
- [x] 5.3 Prepare the playbook for instruction alignment in Phase 2.

## Phase 2 — Harden execution and reduce drift

### 6. Instruction alignment
- [x] 6.1 Align the role-agent instructions with the Phase 1 playbook.
- [x] 6.2 Remove contradictory or obsolete operational guidance.

### 7. Work-item discipline
- [x] 7.1 Define practical use of `change`, `story`, and `bug` under the existing flow.
- [x] 7.2 Define ownership, lock, and dependency expectations.
- [x] 7.3 Define practical WIP / parallelism rules that fit the current team.

### 8. Archive / homologation hardening
- [x] 8.1 Improve consistency of the homologation → archive flow.
- [x] 8.2 Reduce runtime ↔ OpenSpec ↔ metadata drift during closure.
- [x] 8.3 Validate that archived changes finish end-to-end without manual reconciliation whenever possible.

### 9. Validation
- [x] 9.1 Validate Phase 1 on at least one real recent change flow.
- [x] 9.2 Validate that the Kanban remains the easiest primary consultation surface.
- [x] 9.3 Validate that Phase 2 improvements reduce manual reconciliation overhead.


## Reconciliation note
- This umbrella change was superseded on 2026-03-14 by the split changes `standardize-multiagent-kadro-operating-model` (Phase 1) and `harden-multiagent-kadro-execution-model` (Phase 2). Remaining unchecked work was intentionally closed here as superseded so the duplicate umbrella item could leave the active workflow without losing traceability.
