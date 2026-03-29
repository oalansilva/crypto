# Renomear Coluna Homologation

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: not started
- Alan approval: not reviewed

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Renomear coluna "Alan (Stakeholder)" para "Homologation" no Kanban.
- Implementação: Rename já feito em `frontend/src/pages/KanbanPage.tsx` (linhas 1076-1077).
- Design: design.md existe em `openspec/changes/renomear-a-coluna-alan-homologation-para-homologation/design.md`.

## Links
- OpenSpec design: openspec/changes/renomear-a-coluna-alan-homologation-para-homologation/design.md
- PR:
- CI run:

## Notes
- Rename implementado pelo PO agent diretamente no código.
- Design.md confirma que é um rename simples de label.
- DESIGN concluído: design.md existe e está OK.
- Código verificado: `Homologation` aparece em `KanbanPage.tsx` linhas 1076-1077.
- Card movido para "Alan approval" (API offline — atualizado via coordenação).

## Handoff Comment (Kanban)
**feito:** DESIGN completo — rename verificado no código, design.md OK.
**bloqueio:** none.
**próximo passo:** Alan approval → DEV → QA → Homologation.

## Next actions
- [ ] QA: validar visualmente que a coluna aparece como "Homologation" no Kanban
- [ ] Alan approval: aprovar para finalizar
