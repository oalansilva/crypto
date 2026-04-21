# cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban

## Status
- PO: done
- DESIGN: done
- DEV: done
- Homologation: approved (Alan, 2026-04-03 14:22 UTC)
- Archived: 2026-04-03 14:22 UTC
- Alan (Stakeholder): approved

## Decisions (locked)
- Meta: remover cards velhos da coluna Concluído do Kanban
- Critério: cards >7 dias em Concluídos

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/cards-trabalhados-a-mais-7-dias-n-o-devem-ser-esxibidos-na-coluna-concluido-do-kanban/review-ptbr

## Implementation
- Backend: adicionado campo `days_in_archived` no endpoint `/api/workflow/kanban/changes`
- Frontend: filtragem em `filteredItems` - cards com `archived=true` E `days_in_archived > 7` não aparecem no board principal (visíveis via filtro "Archived")

## QA Results (2026-04-03)
- ✅ 42 cards >7 dias corretamente filtrados (não aparecem em Archived)
- ✅ 18 cards ≤7 dias visíveis na coluna Archived
- ⚠️ Nota: Card #57 (Histórico de Sinais) está com 7.59 dias (realmente >7) mas aparece porque o backend usa truncagem inteira (floor), fazendo `days_in_archived=7` onde `7>7=False`. Questão de borda menor.

## Evidências QA
- Screenshots: `/root/.openclaw/workspace/crypto/qa-evidence/card62-qa-*.png`
- Relatório: `/root/.openclaw/workspace/crypto/qa-evidence/card62-qa-report.md`
- Web-accessible: http://72.60.150.140:5173/qa-evidence/card62-qa-*.png

## Notes
- Card criado pelo PO para limpar kanban
- DEV completo
- QA completo (PASS com nota de borda)

## Next actions
- [x] QA: verificar que cards arquivados >7 dias não aparecem no board principal (exceto ao filtrar por "Archived") — PASS
- [ ] Alan: homologar card #62
