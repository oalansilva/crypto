# orden-execu-o-dos-cards

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved


## Closed

- Homologated by Alan and archived.

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
- Delivery validated in runtime by QA with published evidence for board action, drawer action, and refresh persistence.
- Alan homologation approved in chat; change is ready to archive.

## Next actions
- [x] Archive the change after Alan homologation approval.
