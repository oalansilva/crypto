# Proposal — harden-multiagent-kadro-execution-model

## Why

Once the current operating model is standardized, the next problem is execution hardening: reducing manual reconciliation, improving work-item discipline, and making closure behavior more reliable.

This follow-up change exists so the project can harden execution **without mixing that work into the initial standardization change**.

## What changes

This change defines **Phase 2 only**:
- align current role-agent instructions with the standardized operating playbook
- improve disciplined use of `change`, `story`, `bug`, locks, dependencies, ownership, and practical WIP rules
- harden homologation/archive execution behavior
- reduce runtime ↔ OpenSpec ↔ metadata drift
- reduce manual reconciliation overhead after stage transitions and closure

## In scope
- instruction alignment
- work-item discipline
- ownership/locks/dependencies refinement
- homologation/archive hardening
- drift reduction between runtime and OpenSpec-derived metadata

## Out of scope
- replacing the current Kadro/Kanban flow
- replacing the current persistent role agents
- redefining the Phase 1 operating contract from scratch

## Dependency
This change depends on the Phase 1 operating-standardization change being completed first.

## Success criteria
- the current team operates with less manual reconciliation
- the closure flow is more reliable end-to-end
- work-item execution inside a change becomes more disciplined
- the current stage model remains intact while the execution engine becomes more robust
