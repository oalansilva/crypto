# renomear-coluna-alan-approval-para-approval

## Status
- PO: done
- DESIGN: done
- DEV: done
- QA: done
- Alan (Stakeholder): approved
- Homologation: approved ✅
- Archived: ✅ (2026-04-03 12:16 UTC)

## Decisions (locked)
- Meta: renomear coluna "Alan approval" para apenas "Approval"
- Motivação: clareza e consistência no kanban

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/renomear-coluna-alan-approval-para-approval/proposal
- PT-BR review: http://72.60.150.140:5173/openspec/changes/renomear-coluna-alan-approval-para-approval/review-ptbr

## Notes
- Card simples de renomeação
- DEV corrigiu a renderização residual do gate/status no Kanban e no drawer, consolidando aliases legados (`Alan approval`, `Alan (Stakeholder)`, `Alan homologation`) no frontend
- Commit DEV: `ba84797` — `fix: normalize legacy kanban gate labels`
- Checks DEV: `npm --prefix frontend run build` OK; `npx playwright test tests/e2e/kanban-loads.spec.ts -g "legacy gate labels"` OK
- QA revalidou após restart obrigatório (`./stop.sh && ./start.sh`) e o fluxo passou sem regressão no cenário legado
- Check QA: `cd frontend && npx playwright test tests/e2e/kanban-loads.spec.ts -g "legacy gate labels"` OK

## Next actions
- [ ] Alan: homologar o Card #64 em Homologation
