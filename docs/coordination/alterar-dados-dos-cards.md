# alterar-dados-dos-cards

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done
- QA: in progress
- Alan homologation: not reviewed

## Decisions
- `cancelar` card significa retirar do fluxo ativo **sem exclusão física** do registro.
- A primeira entrega deve privilegiar UX enxuta no detalhe/drawer atual do Kanban, evitando tela separada.
- Edição de `title`/`description` não deve trocar o id do card nem resetar histórico/gates.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/alterar-dados-dos-cards/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/alterar-dados-dos-cards/review-ptbr
- Design: http://72.60.150.140:5173/openspec/changes/alterar-dados-dos-cards/design
- Tasks: http://72.60.150.140:5173/openspec/changes/alterar-dados-dos-cards/tasks

## Notes
- PO/DESIGN elaboraram o pacote inicial completo (proposal/review/design/tasks/specs) para destravar a aprovação.
- Ao reconciliar o runtime/Kanban após publicar o pacote completo, a change apareceu corretamente em `Alan approval` com `PO=approved` e `DESIGN=approved`.
- Há uma questão de implementação em aberto para DEV/QA validar depois: como representar cards cancelados no board padrão sem quebrar a leitura do fluxo ativo.
- DEV 2026-03-14 12:14 UTC: drawer do Kanban agora ganhou formulário para editar `title`/`description` e ação explícita de cancelar card via transição para `Archived`, reaproveitando o PATCH existente de workflow. Build frontend ok; testes backend de workflow/kanban relevantes seguem verdes.
- DEV 2026-03-14 12:36 UTC: cobertura frontend/E2E mínima concluída em `frontend/tests/e2e/kanban-card-editing.spec.ts`, validando edição de título/descrição sem trocar `change_id` e cancelamento via `Archived`. `npm run test:e2e -- tests/e2e/kanban-card-editing.spec.ts` e `npm run build` passaram.
- Handoff DEV → QA 2026-03-14 12:36 UTC: pronto para validação funcional. QA deve confirmar no fluxo real que (1) editar preserva id/gates/comments, (2) cancelar remove do fluxo ativo e aparece em `Archived`, (3) o drawer não perde consistência após refresh/reload.
- QA 2026-03-14 12:49 UTC: edição passou no runtime real, mas o cancelamento do próprio card encontrou bloqueio operacional ao tentar persistir `Archived`; o card permaneceu ativo e o gate não avançou naquele turno.
- DEV 2026-03-14 13:06 UTC: bug funcional do cancelamento corrigido separando `cancel_archive=true` do archive formal de change homologada. Validação local+runtime concluída com sucesso (`backend/tests/integration/test_workflow_kanban_manual_backlog.py`, `frontend/tests/e2e/kanban-card-editing.spec.ts`, `npm run build`, smoke real com card temporário cancelado e persistido em `Archived`).
- Reconciliação operacional 2026-03-14 15:58 UTC: o item segue no runtime/Kanban em `DEV` por política, não por defeito funcional. `./scripts/verify_upstream_published.py --for-status QA` ainda bloqueia a promoção por mudanças locais/publicação pendente misturadas no repositório (inclusive fora desta change). Mantido escopo limpo neste turno: sem mexer em trabalho alheio, sem forçar bypass do guard. Próximo gate operacional é publicar/reconciliar o conjunto relevante e então promover `DEV -> QA` para reexecução final da validação no próprio card.
- Reconciliação/publicação 2026-03-14 16:19 UTC: a change foi isolada com segurança do restante do trabalho local, o commit relevante foi publicado em `origin/main` (`82fefba`), e `./scripts/verify_upstream_published.py --for-status QA` passou sem bypass. Com isso, o runtime/Kanban foi promovido corretamente de `DEV` para `QA` e o handoff operacional foi entregue para revalidação final do próprio card no runtime real.

## Next actions
- [x] Publicação/reconciliação: limpar/publicar o conjunto de mudanças relevantes para o `upstream_guard` permitir entrada em `QA` sem bypass inseguro.
- [ ] QA: reexecutar no próprio card a checagem final de edição + cancelamento no runtime agora que a change já está em `QA`, e anexar a evidência conclusiva.
