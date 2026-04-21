# Multi-Agent Operating Playbook

This playbook defines the team contract for the current `crypto` multi-agent model without using Kanban as the operational surface.

## Scope

This process standardizes:
- workflow DB = runtime source of truth
- `docs/coordination/*.md` + OpenSpec = live coordination and evidence surface
- persistent agents remain `main`, `PO`, `DESIGN`, `DEV`, and `QA`

OpenSpec defines change artifacts such as `proposal.md`, `specs/**`, `design.md`, and `tasks.md`, but it does not prescribe role ownership for those files. Role ownership is a local convention.

## Core rules

1. A stage is complete only when **both** are true in the same turn:
   - runtime status reflects the transition
   - the acting role publishes handoff details in the `docs/coordination/<change>.md` note
2. OpenSpec artifacts alone do not complete a stage.
3. If runtime and coordination notes disagree, runtime wins and the mismatch must be reconciled.
4. Main chat with Alan stays managerial; operational detail belongs in runtime state and change coordination notes.
5. A blocked stage must state what is blocked, what evidence exists, and who owns the next step.
6. **Approval checklist (always):** when asking Alan for approval include: (1) PT-BR summary, (2) OpenSpec links (proposal/review-ptbr/tasks), (3) explicit next step.
7. **PO pull rule:** when no active change exists (all are archived), PO must pull the highest-priority change in `Pending` and start planning in the next turn.
8. **Agent auto-trigger rule:** whenever status changes, trigger the owner of the next stage. Example: `PO -> DESIGN` triggers DESIGN; `PO -> DEV` can trigger DEV when design is skipped.

## Role responsibilities

### `main`
- Keeps Alan communication short, managerial, and decision-oriented.
- Uses runtime state + coordination notes as primary sources.
- Triggers or routes the next owner instead of becoming the detailed operational log.
- Must not use chat as the only operational handoff surface.

### `PO`
- Owns scope, acceptance boundaries, and planning completeness.
- Produces and reconciles all change planning artifacts: `proposal.md`, `specs/**`, `design.md` when needed, `tasks.md`, and `review-ptbr.md`.
- Publishes viewer/review links and next-owner direction in the same turn.
- Must not release implementation without recorded Alan approval.

### `DESIGN`
- Owns UX interpretation, prototypes, visual decisions, and design-specific acceptance notes when UI work exists.
- Publishes prototype paths/links and key design decisions required by DEV/QA.
- Must not skip unresolved UX decisions that affect implementation or QA expectations.

### `DEV`
- Owns implementation, local verification, and runtime-aware delivery handoff.
- Keeps coordination notes updated with what changed and where to review it.
- Leaves a structured handoff with evidence and explicit QA/next-owner ask.
- Must not claim DEV complete from files/commits alone.

### `QA`
- Owns validation, regression judgment, and go/no-go recommendation for the next gate.
- Validates against acceptance criteria, runtime behavior, and supplied evidence.
- Creates or preserves blocking `bug` when a defect is real.
- Must not approve based only on intent or code inspection without explicit validation evidence.
- **Must run QA UI checklist** (`docs/qa-ui-checklist.md`) before sending to Homologation.
- **Must run E2E tests for new UI features** (`frontend/tests/*.spec.ts`).

## Standard change handoff contract

Every stage handoff should be short and structured.

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

## Definition of Done by status

### `Pending`
- Runtime has a change entry with clear title/description for PO triage.
- Planning artifacts are not required yet.

### `PO`
- Planning package is materially complete for the current phase.
- Viewer/review links are available.
- Handoff gives Alan or the next owner an explicit review target.

### `DESIGN`
- Required only when UI/UX clarification or prototype work is needed.
- Prototype/decision package exists and is linked in the handoff.
- If skipped, skip reason is explicit in coordination artifacts/runtime notes.

### `Alan approval`
- Alan approval is recorded in the active handoff trail.
- Handoff states what was approved and what stage opens next.

### `DEV`
- Approved scope is implemented for the current phase.
- Relevant artifacts/docs/code are updated.
- Handoff includes evidence and a QA-ready or next-owner-ready next step.

### `QA`
- Validation result is explicit: pass or blocked.
- Evidence or blocker/bug reference is attached in the handoff.
- Runtime status reflects whether the change advances or returns for rework.

### `Homologation`
- QA is complete and evidence is linked.
- Alan receives the managerial summary and exact approval ask.

### `Archived`
- Homologation is complete.
- OpenSpec archive step is done.
- Runtime and coordination no longer show the change as active.

## Completion rule by stage

A stage is not complete until the acting role performs **both** actions:
1. update runtime status
2. publish the matching handoff in `docs/coordination/<change>.md`

If only one happened, the stage remains operationally incomplete and the next turn should reconcile the missing half before continuing.

## Blocked/failure contract

If a handoff cannot proceed, the acting role must include:
- blocker
- evidence already collected
- unblock owner
- whether runtime stays in current stage or returns for rework

## Coordination rule

`docs/coordination/*.md` is the live handoff layer.

Use it to:
- publish stage handoffs
- preserve readable history
- support audits and reconciliação

When drift exists:
- trust runtime first
- reconcile coordination notes immediately in the same turn
- do not reverse runtime state to match stale notes

## Publish sequencing rule

- Preferred sequence for workflow changes: **DEV implements -> QA validates -> publish after QA**.
- Local unpublished changes from the current change should not, by themselves, block `DEV -> QA`.
- If publish/upstream guard is required for later transitions (for example `QA -> Homologation` or `Homologation -> Archived`), do the commit/publish at that later point.
- `DEV -> QA` for runtime/API/UI changes is only complete after a live reconcile/smoke step is documented in the handoff.
- `QA -> Homologation` must distinguish: **QA functional status**, **publish/reconcile state**, and **runtime stage**.
- Do not announce “ready for homologation” unless all three are aligned.

## Practical turn checklist

### Before claiming a stage done
- confirm runtime status
- update the relevant artifacts
- publish the structured handoff in coordination notes
- confirm the next owner is explicit

### Before starting a new turn after drift/blocker
- reconcile runtime first
- then reconcile coordination notes if needed
- only then continue with fresh work
