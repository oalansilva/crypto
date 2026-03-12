## Why

A change-level QA tracking artifact is needed for ongoing UI/browser regression coverage executed with Playwright in the crypto product. The runtime source of truth is the workflow DB + Kanban comments/work items, while OpenSpec should keep a lightweight artifact trail aligned with that runtime state.

## What Changes

- Establish this change as the QA tracking surface for Playwright regression passes.
- Record the current QA scope around wallet/UI smoke validation and evidence links.
- Keep OpenSpec artifacts synchronized with the runtime/Kanban state for this change.

## Scope

In scope:
- QA regression execution for approved DEV changes already in the QA stage.
- Playwright evidence capture and linking.
- Runtime/OpenSpec reconciliation when tracking drifts.

Out of scope:
- New product features.
- DEV implementation unrelated to QA validation.
- Using legacy coordination markdown as the operational source of truth.

## Success Criteria

- Runtime/Kanban and OpenSpec are consistent for this change.
- At least one QA regression step is executed and logged with evidence.
- Short QA handoff/diary note is posted in the runtime comment thread the same turn.
