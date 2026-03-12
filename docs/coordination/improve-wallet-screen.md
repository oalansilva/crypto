# improve-wallet-screen

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved

## Decisions (draft)
- PO artifacts already exist and are complete for this change: proposal, design, tasks, review-ptbr, and wallet-screen spec.
- UI/design coverage is already defined and prototyped at `frontend/public/prototypes/improve-wallet-screen/`.
- Alan approval for proposal/prototype was given in runtime comments; current operational gate is QA revalidation after the prototype redirect fix.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/improve-wallet-screen/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/improve-wallet-screen/review-ptbr

## Notes
- Coordination card created automatically in the same turn as the change.
- Legacy coordination kept here only as a mirrored artifact; runtime source of truth is workflow DB + Kanban.
- QA blocker recheck 2026-03-12: the previously reported blank prototype URL is no longer reproducible. Both `http://72.60.150.140:5173/prototypes/improve-wallet-screen/` and `/index.html` return the prototype.
- Runtime/Kanban update 2026-03-12: QA revalidation proceeded and **failed for visual fidelity**. Active runtime bug: `7d692da9-8646-46e6-99d8-919870b785b3` (`QA: /external/balances diverge visualmente do protótipo aprovado`). Runtime/Kanban is currently back in **DEV** for the desktop composition fix; next step after this DEV turn is QA rerun.
- QA rerun 2026-03-12 08:58 UTC: shell/header e hierarchy ficaram mais próximos do protótipo, mas a implementação ainda falha no comparativo visual. Principal divergência real desta rodada: no desktop o bloco principal de conteúdo ficou comprimido/estreito à esquerda, deixando grande área vazia à direita e quebrando a composição aprovada; mobile segue mais próximo, porém ainda mais denso/apertado que o protótipo. Evidências desta rodada: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12/{proto-desktop,impl-desktop,proto-mobile,impl-mobile}.png`. Runtime permaneceu com o bug `7d692da9-8646-46e6-99d8-919870b785b3` ativo até este novo ajuste DEV.

- DEV follow-up 2026-03-12 09:10 UTC: ajustei novamente `/external/balances` focando exatamente no blocker reconciliado. Desktop: reduzi a coluna do ativo e a densidade do painel `Balances` para evitar o aspecto comprimido/estreito à esquerda e reaproximei o espaçamento do protótipo. Mobile: aliviei os cards (ícone, paddings, gaps e mini-cards) para ficarem menos apertados e mais próximos da referência aprovada. Build frontend ok e novas evidências locais: `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-desktop.png` e `frontend/qa_artifacts/playwright/improve-wallet-screen/devfix-mobile.png`. Próximo passo operacional agora volta a ser **QA rerun**.

- QA rerun 2026-03-12 09:58 UTC: **falhou novamente** após o follow-up DEV de 09:39 UTC. O shell/header e a hierarquia geral ficaram melhores, e mobile ficou aceitável/mais próximo da referência, mas o desktop ainda reprova no comparativo visual: o container principal de `/external/balances` segue comprimido no canto superior esquerdo, com grande área vazia à direita/abaixo, então a composição aprovada do protótipo ainda não foi atingida. Sem blocker novo: permanece ativo apenas o bug `7d692da9-8646-46e6-99d8-919870b785b3`. Evidências desta rodada: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-0955/{proto-desktop.png,impl-desktop-loaded.png,proto-mobile.png,impl-mobile-loaded.png}`.
- DEV follow-up 2026-03-12 10:10 UTC: encontrei e corrigi a causa do desktop ainda parecer comprimido à esquerda. No shell da carteira, os wrappers de header e conteúdo estavam com largura de 1120px mas sem centralização efetiva no layout computado; no viewport 1440px eles renderizavam em `x=0`, colados no canto esquerdo. Ajustei `frontend/src/components/AppNav.tsx` e `frontend/src/pages/ExternalBalancesPage.tsx` para usar `style={{ width: 'min(1120px, calc(100% - 28px))', marginInline: 'auto' }}` e alinhei a altura mínima do painel `Balances` desktop para `lg:min-h-[642px]` em `frontend/src/pages/ExternalBalancesPage.tsx`, espelhando melhor a composição do protótipo aprovado. Build frontend ok (`npm run build`) e evidências DEV desta rodada: `frontend/qa_artifacts/playwright/improve-wallet-screen/devrerun-desktop.png` e `frontend/qa_artifacts/playwright/improve-wallet-screen/devrerun-mobile.png`. Próximo passo operacional: **QA rerun** focando a fidelidade visual final do desktop vs `frontend/public/prototypes/improve-wallet-screen/`.
- DEV validation 2026-03-12 10:40 UTC: reconciliei o runtime/Kanban antes de qualquer trabalho novo e confirmei que a change já está novamente na coluna **QA** com gate `DEV=approved`, preservando o bug ativo `7d692da9-8646-46e6-99d8-919870b785b3` como contexto do rerun. Revalidei localmente o layout computado de `/external/balances` no viewport 1440×900 após o fix: header `x=160 / width=1120`, conteúdo principal `x=160 / width=1120` e painel `Balances` `x=160 / width=1120 / height=642`, eliminando o estado anterior em que o container renderizava em `x=0`. Também gerei evidência complementar em `frontend/qa_artifacts/playwright/improve-wallet-screen/devturn-desktop-check.png` e confirmei novo build frontend ok (`npm run build`). Handoff operacional desta rodada: **QA rerun desktop/mobile** contra `frontend/public/prototypes/improve-wallet-screen/`, com foco no blocker visual do desktop.
- QA rerun 2026-03-12 10:56 UTC: **PASS**. Revalidei `/external/balances` vs `frontend/public/prototypes/improve-wallet-screen/` em desktop (1440×900) e mobile (390×844) aguardando a hidratação completa antes das capturas. O blocker visual desktop `7d692da9-8646-46e6-99d8-919870b785b3` não reproduz mais: heading `Carteira` voltou para `x=160`, bloco `Balances` em `x=161`, sem overflow horizontal, e a composição geral ficou alinhada com o protótipo aprovado; mobile também ficou consistente/aceitável nesta rodada. Evidências: `frontend/qa_artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-1056/{proto-desktop.png,impl-desktop-loaded.png,proto-mobile.png,impl-mobile-loaded.png,summary.json}`. Runtime/Kanban reconciliado para **Alan homologation**, gate `QA=approved`, e o bug runtime `7d692da9-8646-46e6-99d8-919870b785b3` foi encerrado.

## DEV handoff (2026-03-12)
- Ajuste incremental para aproximar `/external/balances` do protótipo aprovado sem mexer nas outras rotas.
- Shell da rota de carteira agora usa header dedicado no estilo **Crypto Lab** (marca + ações `Exportar` / `Atualizar`) em vez da nav global **Crypto Backtester**.
- A composição da página foi reordenada para seguir o protótipo: cabeçalho com KPI total à direita, cards-resumo, grade de controles/meta line, callout de PnL e painel `Balances` com spacing/hierarquia revisados em desktop + mobile.
- Arquivos principais desta rodada:
  - `frontend/src/components/AppNav.tsx`
  - `frontend/src/pages/ExternalBalancesPage.tsx`
- Evidência DEV local: `frontend/qa_artifacts/playwright/improve-wallet-screen/dev-check-{desktop,mobile}.png`

## Next actions
- [x] DEV: Alinhar `/external/balances` ao protótipo aprovado (`frontend/public/prototypes/improve-wallet-screen/`) e responder no card para nova rodada.
- [x] DEV: Ajustar o container/sizing/layout desktop de `/external/balances` para eliminar o aspecto comprimido à esquerda e bater com a composição aprovada do protótipo.
- [x] QA: Reexecutar a validação visual desktop/mobile após o novo ajuste DEV/validação final. (PASS em 2026-03-12 10:56 UTC.)
- [ ] Alan: Homologação final após QA confirmar. (Próximo gate operacional.)

## Closed
- Homologated by Alan and ready for archive.
