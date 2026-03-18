# Proposal — standardize-multiagent-kadro-operating-model

## Why

The current `crypto` operating model already has the correct structural foundation: Kadro/Kanban, workflow DB, OpenSpec, and the persistent role agents `main`, `PO`, `DESIGN`, `DEV`, and `QA`.

The immediate problem is operational inconsistency, not missing architecture. The system needs a smaller first change focused on standardizing how the existing team works before any deeper execution hardening starts.

## What changes

This change defines **Phase 1 only**:
- explicit responsibilities for `main`, `PO`, `DESIGN`, `DEV`, and `QA`
- standard Kanban handoff/comment contract
- Definition of Done per Kanban column
- explicit rule that a stage only counts as complete when runtime/Kanban state and handoff comment are both updated
- explicit demotion of `docs/coordination/*.md` to mirror/audit status instead of active operational truth
- consolidation of these rules into a single operational playbook

## In scope
- process standardization
- handoff standardization
- stage completion rules
- operating playbook consolidation
- preserving current Kadro and current persistent role agents

## Out of scope
- work-item execution hardening
- archive/homologation engine hardening
- lock/dependency/ownership refinement beyond documentation level
- replacing the current Kanban or agent structure

## Success criteria
- the team can execute with clearer stage contracts
- Alan can trust the Kanban more as the primary consultation surface
- fewer stage transitions depend on informal interpretation
- legacy coordination is no longer treated as the live operational source
