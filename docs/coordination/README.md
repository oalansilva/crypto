# Coordination / Change Notes

This folder stores lightweight coordination notes for each OpenSpec change.

Notas de execução atual ficam em `docs/coordination/<change>.md`.
Notas históricas e fechadas foram movidas para `docs/coordination/archive/`.

## Why

Chat messages are ephemeral. These notes provide a shared, versioned view of:
- current status
- decisions
- links
- next actions

## Rules

- If it matters, it must be written down in runtime DB, OpenSpec artifacts, or `docs/coordination/*.md`.
- Keep each file short and actionable.
- Prefer links to evidence (PR, CI runs, OpenSpec viewer) over copied logs.
- `docs/coordination/*.md` é a superfície operacional viva de handoff para o fluxo ativo (ao lado do estado no workflow DB).
- For the standardized role contract, handoff template, and Definition of Done by status, follow `docs/multiagent-operating-playbook.md`.

### Delivery workflow (must follow)

- Always follow the agreed flow: **PO → DESIGN (when UI is involved) → Alan approval → DEV → QA → Homologation → archive**.
- If a change is already open and Alan requests a small adjustment, DEV may implement it within the same change, but QA validation + homologation + archive remain mandatory.

### Autonomy & turn-based execution

- Default mode is **autonomous**: let the Turn Scheduler pull work without Alan online.
- Default to **one work item per turn** unless Alan explicitly asks for fast mode.
- Pull policy: prefer finishing work **right-to-left by status** (items closest to Archived first) before starting new work.

### Communication policy (Alan)

- Send short summaries only, focused on next step and Alan action needed.
- Do not spam repeated updates for unchanged blocked states.

### Agent communication

- PO/DEV/QA communicate via `docs/coordination/<change>.md` notes (auditable, single place).
- Use mentions with `@PO`, `@DESIGN`, `@DEV`, `@QA`, `@Alan`.
- Keep notes to 1–3 lines for blocker, what changed, and next step.
- Each turn should also scan open mentions in the active change note and respond.

### Pending intake + status policy

- `Pending` is the pre-PO backlog status.
- Runtime DB is the operational source of truth for intake changes.
- Transition actions should always go through the same workflow status path in runtime.
- Raw intake in `Pending` does not require immediate OpenSpec artifacts; proposal/spec/tasks/design are created when PO accepts to `PO`.
- Status transitions must respect one-gate-at-a-time progression unless explicit rework is needed.

### Work-item discipline

- Use `change` as the release container, `story` as the default delivery slice, and `bug` for real defects/blockers.
- Create a separate `story` only when ownership, sequencing, dependency, or visibility really benefits.
- A `story` cannot be considered complete while any child `bug` is still open.
- Default WIP: at most **2 active stories per change** and **1 active story per owner/run** unless explicitly justified.
- Declare dependencies before treating a blocked story as active.

### Tracking consistency

- Preferred publish sequence for workflow changes: **DEV implements -> QA validates -> publish after QA**.
- Unpublished local changes from the current change should not block `DEV -> QA`.
- If publish guard is needed for later gates, run `./scripts/verify_upstream_published.py --for-status <status>` in that gate.
- An agent may claim completion only after both:
  1) runtime status update
  2) coordination handoff update in `docs/coordination/<change>.md`
  3) checklist updates in `openspec/changes/<change>/tasks.md` when changed
- If runtime shows blocker/bug/dependency that is missing from OpenSpec or coordination notes, reconcile before continuing.
- Notify Alan only on milestones and blockers:
  - PO ready for Alan approval
  - DEV ready for QA
  - QA ready for Homologation
  - real blocker needing Alan action

### Archiving rule

- After Alan says “ok pode arquivar,” validate and close notes first:
  - gates satisfied in `docs/coordination/<change>.md` (PO/DEV/QA done, Alan approval approved)
  - `openspec/changes/<change>/tasks.md` has no unchecked items
  - handoff marks homologation approved
- Then run `openspec archive ...`.
- Helper script (recommended): `scripts/archive_change_safe.sh <change>`

## Prereqs (so Turn Scheduler works)

- PO/DEV/QA operate in timeboxed turns, 24/7 where configured.
- Notify Alan only when needed: decision required, blocker, CI failed, ready for homologation, or production risk.
- If waiting on Alan, mark the change as `blocked: waiting Alan` and add a next action owned by Alan.

## Recommended definitions

- Use P0/P1/P2 priorities.
- Prefer one change active at a time when possible.
- Merge: default merge commit.
- Production = `main`; deploy via `./stop.sh` + `./start.sh`.
- If production breaks, prefer revert on `main` before a follow-up fix.

For each active change file (`docs/coordination/<change>.md`), ensure:
- Status section is up to date.
- Decisions include non-functional defaults and limits where relevant.
- Links include:
  - OpenSpec viewer
  - PT-BR review (viewer)
  - PR
  - CI run
- Next actions has one role per checkbox:
  - `[ ] PO:` / `[ ] DEV:` / `[ ] QA:` / `[ ] Alan:`

## Arquivos ativos

Atualmente, o fluxo ativo usa apenas arquivos de change criados no diretório raiz desta pasta (ex.: `docs/coordination/<change-name>.md`) + `template.md`.

Arquivos históricos/migrados estão em:

- `docs/coordination/archive`

## Template

Create one file per change:

- `docs/coordination/<change-name>.md`

Suggested structure:

```markdown
# <change-name>

## Status
- PO: (not started|in progress|blocked|done)
- DEV: (not started|in progress|blocked|done)
- QA: (not started|in progress|blocked|done)
- Stakeholder (Alan): (not reviewed|reviewed|approved)

## Decisions (locked)
- ...

## Links
- OpenSpec viewer: ...
- PT-BR review: ...
- PR: ...
- CI run: ...

## Notes
- ...

## Next actions
- [ ] PO: ...
- [ ] DEV: ...
- [ ] QA: ...
- [ ] Alan: ...
```
