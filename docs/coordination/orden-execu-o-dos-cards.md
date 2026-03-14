# orden-execu-o-dos-cards

## Status
- PO: done
- DESIGN: not started
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions
- A ordem visual dos cards dentro da coluna deve representar prioridade operacional real de pull.
- A primeira entrega deve focar em reorder **intra-coluna**; não é mudança de gate/status.
- A operação precisa persistir no runtime/workflow DB e sobreviver a reload.
- Por envolver interação de board em desktop/mobile, o próximo gate correto é DESIGN antes de Alan approval.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/orden-execu-o-dos-cards/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/orden-execu-o-dos-cards/review-ptbr
- Tasks: http://72.60.150.140:5173/openspec/changes/orden-execu-o-dos-cards/tasks

## Notes
- PO package opened from the existing runtime card in `PO` to make the change reviewable and execution-ready.
- Scope stays tight: reorder is about queue priority inside the same stage, not cross-column movement or automatic prioritization.
- Specs created for both `kanban` and `workflow-state-db` so DESIGN/DEV can preserve the runtime-first contract.

## Next actions
- [ ] DESIGN: define the minimal reorder interaction for desktop and mobile, including feedback states and safe constraints for intra-column moves.
