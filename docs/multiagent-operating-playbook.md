# Multi-Agent Operating Playbook

This is the Phase 1 operating contract for the current `crypto` multi-agent model.

## Scope

This playbook standardizes how the existing team operates without changing the current structure:
- workflow DB = runtime source of truth
- Kanban = primary consultation and handoff surface
- OpenSpec = artifact/documentation layer
- persistent agents remain `main`, `PO`, `DESIGN`, `DEV`, and `QA`
- `docs/coordination/*.md` remains mirror/audit support only

## Core rules

1. A stage is complete only when **both** are true in the same turn:
   - runtime/Kanban state reflects the transition
   - the acting role leaves a handoff/comment on the Kanban card
2. OpenSpec artifacts alone do not complete a stage.
3. If runtime/Kanban and `docs/coordination/*.md` disagree, runtime/Kanban wins.
4. Main chat with Alan stays managerial; operational detail belongs in Kanban comments, runtime state, and OpenSpec.
5. A blocked stage must say what is blocked, what evidence exists, and who owns the next step.
6. **PO pull rule:** When no active change exists (all are archived), the PO must automatically pull the highest priority card from the Pending column and start planning in the next turn.
7. **Agent auto-trigger rule:** Whenever a card changes column, the responsible agent for the new stage must be automatically triggered/invoked. E.g., card moves to PO → trigger PO agent; card moves to DEV → trigger DEV agent; card moves to QA → trigger QA agent.

## Role responsibilities

### `main`
- Keeps Alan communication short, managerial, and decision-oriented.
- Uses Kanban/runtime as the primary consultation surface.
- Triggers or routes the next owner instead of becoming the operational log.
- Must not use Telegram chat as the detailed handoff surface.

### `PO`
- Owns scope, acceptance boundaries, typed work-item framing, and planning completeness.
- Produces and reconciles `proposal.md`, `specs/**`, `design.md` when needed, `tasks.md`, and `review-ptbr.md`.
- Publishes viewer/review links in the same turn that planning is handed off.
- Must not release implementation without recorded Alan approval.

### `DESIGN`
- Owns UX interpretation, prototypes, visual decisions, and design-specific acceptance notes when UI work exists.
- Publishes prototype paths/links and any key design decisions required by DEV/QA.
- Must not silently skip unresolved UX decisions when they affect implementation or QA expectations.

### `DEV`
- Owns implementation, local verification, and runtime-aware delivery handoff.
- Updates the minimum instructions/docs/artifacts needed to make the operating contract executable.
- Leaves a structured handoff with changed surfaces, evidence, and explicit QA/next-owner ask.
- Must not claim DEV complete from files/commits alone.

### `QA`
- Owns validation, regression judgment, and go/no-go recommendation for the next gate.
- Validates against acceptance criteria, runtime behavior, and supplied evidence.
- Opens or preserves blocking bugs/work items when a defect is real.
- Must not approve based only on intent or code inspection without explicit validation evidence.

## Standard Kanban handoff/comment contract

Every stage handoff/comment should be short and structured.

### Required fields
- `Status:` pass / blocked / needs-review
- `What changed:` 1-3 bullets or one compact sentence
- `Evidence:` tests, artifact paths, screenshots, links, or `docs-only`
- `Next owner:` `@PO` / `@DESIGN` / `@DEV` / `@QA` / `@Alan`
- `Next step:` the exact follow-up expected

### Canonical template

```text
[ROLE] handoff YYYY-MM-DD HH:MM UTC
Status: pass | blocked | needs-review
What changed: ...
Evidence: ...
Next owner: @ROLE
Next step: ...
```

### Minimum evidence by role
- `PO`: relevant viewer/review links plus any locked scope/acceptance decision
- `DESIGN`: prototype path/link and the design decision being handed off
- `DEV`: implementation/test/doc paths, command results, or `docs-only` when no runtime behavior changed
- `QA`: validation scope, result, and the evidence bundle or blocker/bug reference

## Definition of Done by Kanban column

### `Pending`
- Card exists in runtime/Kanban with enough title/description for PO triage.
- No planning artifacts are required yet.

### `PO`
- Planning package is materially complete for the current phase.
- Viewer/review links are available.
- PO handoff/comment tells Alan or the next role exactly what to review.

### `DESIGN`
- Required only when UI/UX clarification or prototype work is needed.
- Prototype/decision package exists and is linked in the handoff.
- If skipped, the skip reason is explicit in the artifacts/runtime context.

### `Alan approval`
- Alan approval is recorded in the operational trail.
- Handoff/comment states what was approved and what stage opens next.

### `DEV`
- Approved scope is implemented for the current phase.
- Relevant artifacts/docs/code are updated.
- DEV leaves evidence plus a QA-ready or next-owner-ready handoff.

### `QA`
- Validation result is explicit: pass or blocked.
- Evidence or blocker/bug reference is attached in the handoff/comment.
- Runtime reflects whether the change advances or returns for rework.

### `Alan homologation`
- QA has already completed or explicitly handed off a non-QA case if applicable.
- Alan has the managerial summary and knows the exact approval ask.

### `Archived`
- Alan homologation is complete.
- OpenSpec archive step is done.
- Runtime/Kanban and artifacts no longer show the change as active.

## Completion rule by stage

A stage is not complete until the acting role performs **both** actions:
1. update runtime/Kanban to the correct state
2. publish the matching handoff/comment

If only one happened, the stage remains operationally incomplete and the next turn should reconcile the missing half before new work continues.

## Blocked/failure contract

If a handoff cannot proceed, the acting role must leave a comment containing:
- the blocker
- the evidence already collected
- the owner of the unblock
- whether runtime stays in the current stage or moves backward for rework

## Legacy coordination rule

`docs/coordination/*.md` is a readable mirror/audit layer.

Use it to:
- mirror important decisions and milestones
- preserve readable history
- support audits/reconciliation

Do not use it as the deciding live surface for:
- active ownership
- current gate truth
- QA evidence exchange
- agent-to-agent handoffs

When drift exists:
- trust workflow DB/Kanban first
- reconcile the mirror later
- do not reverse runtime decisions to match stale coordination markdown

## Publish sequencing rule

- Preferred sequence for workflow changes: **DEV implements -> QA validates -> commit/publish after QA**.
- Local unpublished changes from the current change should not, by themselves, block `DEV -> QA`.
- If publish/upstream guard is required for later transitions (for example `QA -> Alan homologation` or `Alan homologation -> Archived`), do the commit/publish at that later point, not as an early blocker right after DEV.
- `DEV -> QA` for runtime/API/UI changes is only operationally complete after a live reconcile/smoke step is called out in the handoff.
- `QA -> Alan homologation` must distinguish three things explicitly: **QA functional**, **publish/reconcile**, and **runtime stage**.
- Do not announce “ready for homologation” unless all three are aligned.

## Practical turn checklist

### Before claiming a stage done
- confirm the runtime/Kanban column and gate state
- update the relevant artifact(s)
- publish the structured handoff/comment
- confirm the next owner is explicit

### Before starting a new turn after drift/blocker
- reconcile runtime first
- then reconcile the mirror/audit docs if needed
- only then continue with fresh work
