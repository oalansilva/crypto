# Design — standardize-multiagent-kadro-operating-model

## Overview

This is a process-first change.

It preserves:
- the current Kadro / Kanban stage model
- the current persistent agents (`main`, `PO`, `DESIGN`, `DEV`, `QA`)
- workflow DB as runtime source of truth
- OpenSpec as artifact layer

## Design principle

> First standardize how the current system is operated. Do not harden the execution engine until the operating contract is clear.

## Main design decisions

### 1. Keep the current structure
No new persistent agents are introduced in this change.
No Kanban redesign is required.

### 2. Standardize handoffs
Each stage transition should leave a short, structured handoff/comment that includes:
- status
- what changed
- evidence
- next owner / next step

### 3. Make stage closure explicit
A stage must not count as complete unless:
- runtime/Kanban state reflects the transition
- the relevant operational handoff/comment exists

### 4. Demote legacy coordination
`docs/coordination/*.md` should remain as mirror/audit support, not as the deciding operational surface for live work.

### 5. Produce a reusable playbook
The output of this change should be reusable by all current agents as the common operating contract.
