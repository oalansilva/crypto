# align-agent-instructions-workflow-db

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: skipped
- QA: skipped
- Alan homologation: approved

## Decisions (draft)
- Goal: align all agent instructions with the new workflow DB model.
- Runtime source: workflow DB + Kanban.
- OpenSpec remains artifact/documentation.
- Typed work items and parallel work rules must be reflected in instructions.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/align-agent-instructions-workflow-db/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/align-agent-instructions-workflow-db/review-ptbr

## Notes
- Change criada porque Alan apontou que cada agente tem seus próprios arquivos/instruções e todos precisam ser alinhados ao novo modelo.
- PO reconciled tracking: `proposal.md`, `design.md` e `specs/agent-instruction-alignment/spec.md` já registram os arquivos/assunções do modelo antigo e a redação canônica para runtime source, handoff, paralelismo e work items tipados; `crypto/AGENTS.md` também já reflete esse alinhamento.
- A maior parte do trabalho foi absorvida diretamente por edições aplicadas nos arquivos de instrução/memória do workspace e dos agentes; por decisão do Alan, a change foi encerrada administrativamente como supersedida por essas edições diretas.

## Closed
- Archived after direct instruction alignment was already applied across workspace/agent layers.

## Next actions
- [x] PO: Formalizar a proposta de alinhar as instruções dos agentes.
- [x] PO: Reconciliar tracking entre coordination e OpenSpec tasks.
- [ ] Alan: Revisar e aprovar a proposta.
- [ ] DEV: Atualizar os arquivos de instrução após aprovação.
- [ ] QA: Revisar consistência depois.
