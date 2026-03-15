# reduce-workflow-scheduler-polling

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions
- O scheduler deve ser mais orientado a evento real e menos a polling repetido.
- Turnos sem mudança material devem ser suprimidos para reduzir custo de tokens.
- Notificações repetidas sem mudança de estado devem continuar proibidas.
- DESIGN foi marcado como skipped porque o ajuste é de comportamento operacional, não de UI.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/reduce-workflow-scheduler-polling/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/reduce-workflow-scheduler-polling/review-ptbr
- Tasks: http://72.60.150.140:5173/openspec/changes/reduce-workflow-scheduler-polling/tasks

## Notes
- Change aberta a partir da análise Pareto de consumo de tokens do workflow.

## Next actions
- [ ] Alan: aprovar o pacote de planning para implementação.
