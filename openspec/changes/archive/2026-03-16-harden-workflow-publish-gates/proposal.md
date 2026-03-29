# Proposal — harden-workflow-publish-gates

## Why

We hit a recurring operational failure in the workflow:
- QA functionally validates a change
- but the runtime stage promotion is still blocked by upstream/publish guards
- or the live runtime is stale compared to the already-correct local code

This creates confusing states such as:
- QA approved in practice, but card still stuck in QA
- live/runtime diverging from local validation
- Alan receiving mixed signals about whether the item is truly ready for homologation

## What Changes

- make the DEV → QA handoff explicitly require live/runtime reconciliation when the change affects runtime/API/UI
- make the QA → Homologation transition robust against publish/upstream guard friction
- distinguish clearly between:
  - functional validation result
  - publish/reconcile status
  - runtime stage transition status
- add a small operational rule so a change is only announced as ready for homologation after all three are aligned

## Scope

This change covers:
- workflow/runtime rules for promotion between DEV, QA, and Homologation
- guard-rail behavior when QA is functionally green but publish/runtime is not yet reconciled
- required handoff notes/checks for runtime-affecting changes

This change does not cover:
- rewriting the whole CI system
- removing all safety guards
- changing product functionality unrelated to workflow reliability

## Outcome

After this change, the workflow should stop producing the recurring situation where a change is functionally approved but operationally stuck. The process should make it explicit what is missing and should prevent premature “ready for homologation” signals.
