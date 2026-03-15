# harden-workflow-publish-gates

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions
- O problema a corrigir é de fluxo operacional: QA funcional green pode continuar travada por publish/upstream guard ou runtime stale.
- O fluxo precisa distinguir explicitamente validação funcional, publish/reconcile e stage runtime.
- Mudanças que afetam runtime/API/UI devem ter reconciliação/live smoke antes de o handoff DEV → QA ser considerado operacionalmente completo.
- A mensagem “pronto para homologação” só pode sair quando QA funcional + publish/reconcile + stage runtime estiverem consistentes.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/harden-workflow-publish-gates/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/harden-workflow-publish-gates/review-ptbr
- Tasks: http://72.60.150.140:5173/openspec/changes/harden-workflow-publish-gates/tasks

## Notes
- Change aberta para eliminar a recorrência do bloqueio visto em `numera-o-cards`.
- DESIGN foi marcado como skipped porque o ajuste é de fluxo/ruleset, não de interação visual.

## Next actions
- [ ] Alan: aprovar o pacote de planning para implementar o endurecimento do fluxo.
