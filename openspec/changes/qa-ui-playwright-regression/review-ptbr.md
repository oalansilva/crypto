## Resumo para revisão

Objetivo desta change:
- manter um artefato leve de QA para regressões UI/browser com Playwright no projeto crypto;
- registrar evidências e deixar OpenSpec alinhado com o runtime/Kanban.

Situação atual:
- o fluxo wallet foi revalidado com sucesso na última rodada de QA;
- o blocker anterior era apenas de automação (seletor Playwright ambíguo) e já foi resolvido;
- não houve reprodução de defeito real de produto nesta rodada.

Estado de handoff:
- change pronta para **Alan homologation**;
- `QA=approved`;
- sem blocker ativo no momento.

Evidência principal:
- `qa_artifacts/playwright/wallet/recheck-2026-03-12T1311Z/{00-playwright.log,01-home.png,02-wallet-loaded.png,error-context.md,exit_code.txt}`
