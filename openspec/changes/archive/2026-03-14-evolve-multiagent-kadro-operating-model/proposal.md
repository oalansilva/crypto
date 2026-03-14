# Proposal — evolve-multiagent-kadro-operating-model

## Why

The current `crypto` operating model already has the right structural pieces:
- Kadro / Kanban as the main operational surface
- workflow DB as the runtime source of truth
- OpenSpec as the artifact layer
- persistent role agents (`main`, `PO`, `DESIGN`, `DEV`, `QA`)

The main problem is not missing architecture. The main problem is **operational inconsistency**:
- stages can still drift across runtime, Kanban, OpenSpec, and legacy coordination mirrors
- handoffs are not yet standardized enough
- the main orchestrator still spends too much effort reconciling state manually
- the execution model for `change` / `story` / `bug` / locks / dependencies is not yet consistently applied

This change evolves the operating model **without replacing Kadro or the existing agents**.

## What changes

This change formalizes a two-phase evolution of the current model.

### Phase 1 — standardize the operating model
Phase 1 focuses on process clarity, not engine changes:
- define explicit responsibilities for `main`, `PO`, `DESIGN`, `DEV`, and `QA`
- standardize the Kanban handoff/comment contract
- define Definition of Done per Kanban column
- enforce the rule that a stage is only complete when runtime state + handoff comment are both updated
- demote `docs/coordination/*.md` to mirror/audit status instead of active operational truth

### Phase 2 — harden execution and reduce drift
Phase 2 builds on Phase 1 and improves the execution engine behavior:
- align agent instructions to the Phase 1 playbook
- improve disciplined use of `change`, `story`, `bug`, locks, dependencies, and ownership
- harden homologation/archive completion flows
- reduce runtime ↔ OpenSpec ↔ metadata drift
- refine practical parallelism rules without replacing the existing stage flow

## Goals

### In scope
- Keep the current Kadro/Kanban stage model
- Keep the current role agents
- Improve the operating contract between those agents
- Improve auditability and predictability of stage completion
- Prepare the model for safer parallel execution later

### Out of scope
- Replacing Kadro/Kanban
- Replacing the current agent roster
- Introducing a complex new multi-agent topology immediately
- Introducing a heavy plugin/webhook-first architecture as part of this change
- Replacing workflow DB or OpenSpec

## Success criteria
- Alan can trust the Kanban as the primary consultation surface
- stage completion becomes more predictable and auditable
- manual reconciliation work decreases
- the current team structure remains intact, but operates with clearer rules
- Phase 1 can ship as a small process-first improvement before deeper engine hardening starts in Phase 2
