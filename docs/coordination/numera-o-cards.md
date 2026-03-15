# numera-o-cards

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved

## Decisions
- Cada card deve receber um número sequencial humano e estável para referência rápida no board, QA e conversas.
- O número é identificador, não mecanismo de ordenação; reorder, edição e mudança de coluna não devem renumerar o card.
- A primeira versão não inclui renumeração manual nem numeração por coluna.
- DESIGN foi mantido como skipped porque a mudança é um ajuste pequeno de UI sobre superfícies já existentes.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/numera-o-cards/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/numera-o-cards/review-ptbr
- Tasks: http://72.60.150.140:5173/openspec/changes/numera-o-cards/tasks

## Notes
- Card puxado de Pending para PO e reconciliado com OpenSpec/coordination no mesmo turno para evitar divergência runtime/artifacts.
- PO package fechado sem gate de DESIGN separado; foco é persistência + exibição discreta do número no card/drawer.
- DEV implementou a numeração estável e reconciliou o runtime live; QA validou `card_number: 16` na API e `#16` no board/drawer após reload.
- Alan confirmou em chat que a change está validada; change pronta para archive.

## Next actions
- [x] Archive the change after Alan homologation approval.
