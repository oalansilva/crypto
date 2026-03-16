# Proposal — reduce-workflow-scheduler-polling

## Why

Token analysis showed that a large share of workflow cost is being burned by repeated scheduler turns that re-check unchanged state, spawn follow-up work too often, and perform shell-heavy reconciliation even when there is no new milestone.

## What Changes

- tighten the scheduler so it runs on meaningful events and fewer idle rechecks
- add explicit no-change suppression for repeated unchanged workflow turns
- reduce repeated polling/reconciliation when the board/runtime state has not materially changed
- make scheduler cadence and wake behavior more event-driven for active items

## Scope

This change covers scheduler/turn behavior for workflow orchestration and token efficiency.

This change does not cover feature implementation work, CI redesign, or product UI unrelated to workflow cadence.

## Outcome

After this change, the workflow should spend fewer tokens on idle orchestration and repeated inspections, while still notifying and advancing work when a real milestone, blocker, or gate transition happens.
