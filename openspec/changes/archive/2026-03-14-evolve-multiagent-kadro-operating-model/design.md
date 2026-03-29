# Design — evolve-multiagent-kadro-operating-model

## Overview

This change is a **workflow and operating-model change**, not a UI redesign.

The design principle is:

> preserve the current Kadro + workflow DB + OpenSpec + role-agent structure, and tighten the way the system is operated.

## Operating model to preserve
- Kanban remains the primary operational surface
- workflow DB remains the runtime source of truth
- OpenSpec remains the artifact/documentation layer
- `main`, `PO`, `DESIGN`, `DEV`, and `QA` remain the persistent role agents
- stage order remains:
  - Pending
  - PO
  - DESIGN
  - Alan approval
  - DEV
  - QA
  - Homologation
  - Archived

## Main design decisions

### 1. Process-first before engine-hardening
The change is intentionally split into two phases.

#### Phase 1
Standardize the process:
- explicit role responsibilities
- explicit handoff contract
- explicit Definition of Done per stage
- explicit rule that no stage closes without runtime + handoff update
- explicit demotion of legacy coordination markdown to mirror-only status

#### Phase 2
Harden the execution model:
- align instructions and runtime expectations
- improve story/bug/lock/dependency discipline
- improve ownership and parallelism rules
- harden homologation/archive behavior
- reduce post-hoc reconciliation and metadata drift

### 2. No new persistent agents in this change
The proposal intentionally keeps the existing persistent team.
The goal is to improve operation, not expand the agent roster.

### 3. Keep the main chat managerial
The main orchestrator should continue to summarize milestones, blockers, approvals, and next steps in chat, while technical work stays delegated or isolated.

### 4. Handoff contract as the center of operation
Each stage transition should leave a short, structured Kanban comment with:
- status
- what changed
- evidence
- next owner / next step

This is the minimum unit of coordination that should be required for a stage to count as complete.

## Non-UI impact
This change may require light updates to:
- agent instruction files
- workflow comments/handoff conventions
- archive/homologation consistency rules
- runtime guardrails around stage completion

But it should not require a redesign of the Kanban UI itself in Phase 1.

## Risks
- too much process overhead
- keeping rules spread across too many files
- treating legacy coordination as active truth by habit

## Mitigations
- keep Phase 1 intentionally small
- keep handoffs short and structured
- ship process clarity before engine automation
