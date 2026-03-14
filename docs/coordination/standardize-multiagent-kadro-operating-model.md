# standardize-multiagent-kadro-operating-model

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: not started
- Alan homologation: not reviewed

## Decisions (draft)
- This change covers Phase 1 only: standardize the operating model.
- Preserve the current Kadro / Kanban flow and the current persistent role agents.
- Focus on role contract, handoff contract, Definition of Done, and legacy coordination demotion.
- `docs/coordination/*.md` is mirror/audit support only; workflow DB + Kanban remain the live operational surface.
- A stage only counts as complete when runtime/Kanban and the matching handoff comment are both updated in the same turn.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/standardize-multiagent-kadro-operating-model/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/standardize-multiagent-kadro-operating-model/review-ptbr
- Design: http://72.60.150.140:5173/openspec/changes/standardize-multiagent-kadro-operating-model/design
- Tasks: http://72.60.150.140:5173/openspec/changes/standardize-multiagent-kadro-operating-model/tasks
- Playbook: `docs/multiagent-operating-playbook.md`

## Notes
- This is the process-standardization change and should be completed before the execution-hardening follow-up starts.
- DEV 2026-03-14 00:32 UTC: implemented Phase 1 as a tight documentation/instructions pass. Added `docs/multiagent-operating-playbook.md` consolidating explicit role responsibilities, structured Kanban handoff contract, minimum evidence expectations, Definition of Done by Kanban column, blocked-stage behavior, the rule that a stage only closes with runtime + handoff, and the explicit demotion of `docs/coordination/*.md` to mirror/audit status.
- DEV 2026-03-14 00:32 UTC: aligned `AGENTS.md`, `docs/coordination/README.md`, and `docs/workflow-criar-funcionalidade.md` so the repo instructions point to the same Phase 1 operating contract instead of leaving these rules implicit or scattered.
- DEV handoff: implementation for Phase 1 is complete; next step is QA review for consistency and usability of the new operating playbook/instruction set.

## Next actions
- [x] PO: Review and refine proposal/spec/design/tasks as the formal Phase 1 planning package.
- [x] Alan: Review the planning package and approve before implementation.
- [ ] QA: Review the new playbook/instruction alignment for consistency with the approved Phase 1 scope and confirm no Phase 2 behavior was introduced.
- [ ] Alan: Homologate after QA confirms the operating-model update is coherent.
